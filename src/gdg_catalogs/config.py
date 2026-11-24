import urllib.request, json
from pathlib import Path
import validators
import polars as pl
from .utils import parse_path

def _load_json(path: str) -> dict:
    if validators.url(path):
        with urllib.request.urlopen(path) as url:
            json_config = json.loads(url.read().decode())
    else:
        with open(path) as f:
            json_config = json.load(f)
    return json_config

class Config:
    path_column: str | None = 'path'
    variable_column: str | None = 'variable_id'
    groupby_attrs: list[str] | None = None
    catalog_file: str | None = None
    _auto_groups: bool = False
    _spec: dict | None = None

    def __init__(
        self,
        catalog_path: str | None = None,
        variable_column: str | None = None,
        path_column: str | None = None,
        groupby_attrs: list[str] | None = None
    ):
        if catalog_path is not None:
            catPath = parse_path(catalog_path)
            if catPath.suffix == '.json':
                self._load_json_config(catalog_path)
                spec_cat_path = str(self._spec["catalog_file"])
                self.catalog_file = str(catPath.parent / spec_cat_path)
                else:
                    self.catalog_file = spec_cat_path
            elif catPath.suffix == '.csv':
                self.catalog_file = catalog_path

        if variable_column is not None:
            self.variable_column = str(variable_column)

        if path_column is not None:
            self.path_column = str(path_column)

        if groupby_attrs is not None:
            self.groupby_attrs = groupby_attrs

        # only automatically set groupby_attrs if not supplied _and_ if a csv
        # catalog is provided
        if self.catalog_file is not None:
            if self.groupby_attrs is None:
                self._auto_groups = True

    def _load_json_config(
        self,
        json_path: str
    ) -> None:
        self._spec = _load_json(json_path)
        self.path_column = self._get_path_col()
        aggs = self._get_aggs()
        if aggs is not None:
            self.variable_column = aggs["variable_column_name"]
            if "groupby_attrs" in aggs.keys():
                self.groupby_attrs = aggs["groupby_attrs"]

    def _get_aggs(self):
        if "aggregation_control" in self._spec.keys():
            return self._spec["aggregation_control"]
        else:
            return None

    def _get_path_col(self) -> str:
        return self._spec["assets"]["column_name"]

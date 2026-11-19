import urllib.request, json
from pathlib import Path
import validators
import polars as pl

def _load_json(path):
    if validators.url(path):
        with urllib.request.urlopen(path) as url:
            json_config = json.loads(url.read().decode())
    else:
        with open(path) as f:
            json_config = json.load(f)
    return json_config

class Config:
    path_column: str = 'path'
    variable_column: str = 'variable_id'
    groupby_attrs: list[str] = []
    catalog_file: str = None
    _auto_groups: bool = False

    def __init__(
        self,
        catalog_path=None,
        variable_column=None,
        path_column=None,
        groupby_attrs=None
    ):
        if catalog_path:
            catPath = Path(catalog_path).resolve()
            if catPath.suffix == '.json':
                self._load_json_config(catalog_path)
                spec_cat_path = self._spec["catalog_file"]
                if spec_cat_path.startswith('./'):
                    self.catalog_file = '/'.join(catalog_path.split('/')[:-1])+\
                                        spec_cat_path[1:]
                else:
                    self.catalog_file = spec_cat_path
            elif catPath.suffix == '.csv':
                self.catalog_file = catalog_path

        if variable_column:
            self.variable_column = variable_column

        if path_column:
            self.path_column = path_column

        if groupby_attrs:
            self.groupby_attrs = groupby_attrs

        # only automatically set groupby_attrs if not supplied _and_ if a csv
        # catalog is provided
        if self.catalog_file:
            if not self.groupby_attrs:
                self._auto_groups = True

    def _load_json_config(
        self,
        json_path
    ):
        self._spec = _load_json(json_path)
        self.path_column = self._get_path_col()
        aggs = self._get_aggs()
        if aggs:
            self.variable_column = aggs["variable_column_name"]
            if "groupby_attrs" in aggs.keys():
                self.groupby_attrs = aggs["groupby_attrs"]

    def _get_aggs(self):
        if "aggregation_control" in self._spec.keys():
            return self._spec["aggregation_control"]
        else:
            return None

    def _get_path_col(self):
        return self._spec["assets"]["column_name"]

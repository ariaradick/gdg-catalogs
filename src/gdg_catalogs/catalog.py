from pathlib import Path
import yaml
from .config import Config
from .utils import _to_list, parse_path
import polars as pl
import validators

class Catalog(Config):
    df: pl.DataFrame

    def __init__(
        self,
        catalog_path,
        filter_by=None,
        variable_column=None,
        path_column=None,
        groupby_attrs=None
    ):
        super().__init__(
            catalog_path,
            variable_column=variable_column,
            path_column=path_column,
            groupby_attrs=groupby_attrs
        )
        self.df = pl.read_csv(self.catalog_file)

        if filter_by is not None:
            self.df = self._filter(filter_by)

        if self._auto_groups:
            self.groupby_attrs = self._auto_groupby_attrs()

    def _auto_groupby_attrs(
        self,
        skip_columns=[]
    ):
        skipCol = skip_columns.copy()
        skipCol.append(self.path_column)
        grpCols = []
        for c in self.df.columns:
            if c not in skipCol and self.df.n_unique(pl.col(c)) > 1:
                grpCols.append(c)
        return grpCols

    def _filter(self, filter_by):
        return self.df.filter(
            *[pl.col(k).is_in(_to_list(v)) for k,v in filter_by.items()]
        )

    def search(self, **kwargs):
        return self._filter(kwargs)

    def get_paths(
        self,
        filter_by=None
    ):
        if filter_by is not None:
            df = self._filter(filter_by)
        else:
            df = self.df
        return df.get_column(self.pathColumn).to_list()

def _open_yaml(config_file: str):
    if validators.url(config_file):
        with urllib.request.urlopen(path) as url:
            yaml_conf = yaml.safe_load(url.read().decode())
    else:
        with open(config_file) as f:
            yaml_conf = yaml.safe_load(f)
    return yaml_conf

def _parse_yaml(config_file: str) -> dict:
    yaml_conf = _open_yaml(config_file)

    catalog_file = yaml_conf.get("catalog_file", None)
    if catalog_file is not None:
        yamlPath = parse_path(config_file)
        full_catalog_file_path = str((yamlPath.parent / catalog_file).resolve())
    else:
        full_catalog_file_path = None

    config_dict = {
        "catalog_file": full_catalog_file_path,
        "groupby_attrs": yaml_conf.get("groupby_attrs", None),
        "variable_column": yaml_conf.get("variable_column", None),
        "path_column": yaml_conf.get("path_column", None),
        "filter_by": yaml_conf.get("filter_by", None)
    }
    return config_dict

def from_yaml(
    path_to_yaml,
    **kwargs
):
    config_dict = _parse_yaml(path_to_yaml)
    for k,v in kwargs.items():
        if k in config_dict.keys():
            config_dict[k] = v
    catalog_file = config_dict["catalog_file"]
    del config_dict["catalog_file"]
    return Catalog(
        catalog_file,
        **config_dict
    )

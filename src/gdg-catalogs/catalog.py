import polars as pl
from pathlib import Path
from .config import Config
from .utils import _to_list

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

        if filter_by:
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
        if filter_by:
            df = self._filter(filter_by)
        else:
            df = self.df
        return df.get_column(self.pathColumn).to_list()

import unittest
from pathlib import Path
import gdg_catalogs as gcat

thisDir = Path(__file__).parent.resolve()

class TestGDGCatalogs(unittest.TestCase):

    def test_json(self):
        testcat = gcat.Catalog(thisDir / "test_catalogs" / "catalog.json")

        self.assertEqual(
            testcat.variable_column,
            "var_id"
        )

        self.assertEqual(
            testcat.path_column,
            "filepath"
        )

        self.assertEqual(
            testcat.groupby_attrs,
            [
              "source_id",
              "experiment_id",
              "frequency",
              "table_id",
              "grid_label",
              "realm",
              "member_id",
              "chunk_freq"
            ]
        )

    def test_yamlconf(self):
        testcat = gcat.from_yaml(thisDir / "test_catalogs" / "config.yaml")

        self.assertEqual(
            testcat.variable_column,
            "var_id"
        )

        self.assertEqual(
            testcat.path_column,
            "filepath"
        )

        self.assertEqual(
            testcat.groupby_attrs,
            [
                "experiment_id",
                "realm",
                "frequency",
                "var_id"
            ]
        )

        # test that the filter_by is correctly choosing only one experiment_id
        self.assertEqual(
            int(testcat.df.get_column("experiment_id").n_unique()),
            1
        )

        # test that config options passed as arguments take precedence
        testcat = gcat.from_yaml(
            thisDir / "test_catalogs" / "config.yaml",
            variable_column="variable",
            path_column="wherefile",
            groupby_attrs=["experiment_id", "realm"]
        )

        self.assertEqual(
            testcat.variable_column,
            "variable"
        )

        self.assertEqual(
            testcat.path_column,
            "wherefile"
        )

        self.assertEqual(
            testcat.groupby_attrs,
            [
                "experiment_id",
                "realm"
            ]
        )

    def test_csv(self):
        # note that this is expected to give incorrect seeming results for
        # variable_column, because it will load the default value
        testcat = gcat.Catalog(
            thisDir / "test_catalogs" / "catalog.csv",
            path_column="filepath"
        )

        self.assertEqual(
            testcat.variable_column,
            "variable_id"
        )

        self.assertEqual(
            testcat.path_column,
            "filepath"
        )

        # test the auto groupby_attrs
        self.assertEqual(
            testcat.groupby_attrs,
            [
                'experiment_id',
                'frequency',
                'realm',
                'member_id',
                'var_id',
                'time_range',
                'standard_name',
                'pass_qc',
                'who_qc'
            ]
        )

        # test loading config options passed as arguments
        testcat = gcat.Catalog(
            thisDir / "test_catalogs" / "catalog.csv",
            variable_column="var_id",
            path_column="filepath",
            groupby_attrs=["experiment_id", "realm", "frequency", "var_id"]
        )

        self.assertEqual(
            testcat.variable_column,
            "var_id"
        )

        self.assertEqual(
            testcat.path_column,
            "filepath"
        )

        self.assertEqual(
            testcat.groupby_attrs,
            [
                "experiment_id",
                "realm",
                "frequency",
                "var_id"
            ]
        )

    def test_json_url(self):
        testcat = gcat.Catalog("https://raw.githubusercontent.com/NOAA-GFDL/spear-flp/refs/heads/main/catalog_blue.json")

        self.assertEqual(
            testcat.variable_column,
            "variable_id"
        )

        self.assertEqual(
            testcat.path_column,
            "path"
        )

        self.assertEqual(
            testcat.groupby_attrs,
            [
                "source_id",
                "experiment_id",
                "frequency",
                "table_id",
                "grid_label",
                "realm",
                "member_id",
                "chunk_freq",
                "pass_qc",
                "who_qc"
            ]
        )

if __name__=="__main__":
    unittest.main()

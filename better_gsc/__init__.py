import zipfile
from logging import getLogger, basicConfig, INFO
from pprint import pformat
from tempfile import TemporaryFile
import contextlib
import threading

import matplotlib
from matplotlib import pyplot
import pandas
import click
import flask


matplotlib.use("agg")

logger = getLogger(__name__)

# Matplotlib not threadsafe...
PYPLOT_LOCK = threading.Lock()

SORT_KWARGS = {
    "Dates": {"by": "Date", "ascending": True},
}

PLOT_KWARGS = {
    "Devices": {"kind": "bar"},
    "Pages": {"kind": "barh"},
    "Countries": {"kind": "barh"},
    "Queries": {"kind": "barh"},
}

def get_sorted_df(dataset_name, df):
    kwargs = SORT_KWARGS.get(dataset_name)
    if kwargs is None:
        return df
    else:
        return df.sort_values(**kwargs)


def get_plot(dataset_name, df, column):
    kwargs = PLOT_KWARGS.get(dataset_name, {})
    print(column)
    kwargs["title"] = column
    return df[column].plot(**kwargs)


def ctr_converter(raw):
    # Turn "n+.n+% into a float"
    return float(raw[:-1])


@click.command()
@click.argument("gsc-zipfile", type=click.File(mode="rb"))
def main(gsc_zipfile):
    basicConfig(level=INFO)

    zip_h = zipfile.ZipFile(gsc_zipfile)
    infolist = zip_h.infolist()
    logger.info("opened zipfile, contents: %s", pformat(infolist))

    dfs = {
        info.filename[:-4]: pandas.read_csv(
            zip_h.open(info.filename),
            index_col=0,
            converters={"CTR": ctr_converter}
        )
        for info in infolist
        if info.filename.endswith(".csv")
    }
    logger.info("read %d dataframes: %s", len(dfs), list(dfs.keys()))

    app = flask.Flask("better-gsc", template_folder="better_gsc/templates")

    @app.route("/")
    def index():
        return flask.render_template(
            "index.html",
            dfs=dfs
        )

    @app.route("/dataset/<dataset_name>")
    def dataset(dataset_name):
        return flask.render_template(
            "dataset.html",
            dataset_names=sorted(dfs.keys()),
            dataset_name=dataset_name,
            df=dfs[dataset_name]
        )

    @app.route("/dataset/<dataset_name>/<column>.svg")
    def dataset_graph(dataset_name, column):
        df = get_sorted_df(dataset_name, dfs[dataset_name])
        with PYPLOT_LOCK:
            ax = get_plot(dataset_name, df, column)
            fig = ax.get_figure()

            buf = TemporaryFile()
            fig.savefig(buf, format="svg")
            buf.seek(0)

            with contextlib.closing(pyplot):
                return flask.Response(buf, mimetype="image/svg+xml")


    app.run()


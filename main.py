import sys
from qgis.core import *
from PyQt5.Qt import *
from mainWindow import MapExplorer


def main(argv):
    app = QApplication(argv)
    qgs = QgsApplication([], False)
    qgs.setPrefixPath("C:/OSGeo4W64/apps/qgis", True)
    qgs.initQgis()

    window = MapExplorer()
    window.show()
    window.raise_()

    retval = app.exec_()
    app.deleteLater()
    qgs.exitQgis()
    sys.exit(retval)


if __name__ == "__main__":
    main(sys.argv)

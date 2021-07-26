from qgis.core import *
from qgis.gui import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets

import psycopg2
from psycopg2 import sql
from createTable import createTableWindow
from formDatos import showDatos

class MapExplorer(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.mapCanvas = QgsMapCanvas()
        self.mapCanvas.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.mapCanvas.setCanvasColor(Qt.white)

        self.loadMap()
        self.setupUi(self)

        self.gridLayout.addWidget(self.mapCanvas, 0, 1, 1, 1)

    """
        Funcion para crear la interfaz de la ventana principal
    """
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Explorador")
        MainWindow.setObjectName("Explorador")
        MainWindow.resize(1200, 800)
        MainWindow.setMinimumSize(QtCore.QSize(1200, 800))

        # Widget Central
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        MainWindow.setCentralWidget(self.centralWidget)

        # Barra Menu
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 26))
        self.menuArchivo = self.menubar.addMenu("Archivo")
        self.menuNuevo = self.menubar.addMenu("Nuevo")
        MainWindow.setMenuBar(self.menubar)

        self.actionExit = QtWidgets.QAction("Exit", MainWindow)
        self.actionExit.triggered.connect(qApp.quit)
        self.menuArchivo.addAction(self.actionExit)

        # Widget Lista Capas
        self.listWidget = QtWidgets.QListWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.listWidget.itemClicked.connect(self.showLayer)
        self.listWidget.itemDoubleClicked.connect(self.loadTable)

        layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]

        for layer in layers:
            item = QtWidgets.QListWidgetItem(layer)
            item.setCheckState(Qt.CheckState(2))
            self.listWidget.addItem(item)

        # Widget Opciones
        self.formGroupBox = QtWidgets.QGroupBox("Opciones de Tabla", self.centralWidget)
        self.formGroupBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.formLayout = QtWidgets.QVBoxLayout(self.formGroupBox)

        self.newTable = QtWidgets.QPushButton("Nueva Tabla", self.formGroupBox)
        self.formLayout.addWidget(self.newTable)
        self.newTable.clicked.connect(self.showNewTable)
        self.deleteTableBtn = QtWidgets.QPushButton("Borrar Tabla", self.formGroupBox)
        self.formLayout.addWidget(self.deleteTableBtn)
        self.deleteTableBtn.clicked.connect(self.deleteTable)
        self.saveButton = QtWidgets.QPushButton("Guardar Cambios", self.formGroupBox)
        self.formLayout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.saveTable)
        self.newEntryBtn = QtWidgets.QPushButton("Nuevo Entrada", self.formGroupBox)
        self.formLayout.addWidget(self.newEntryBtn)
        self.newEntryBtn.clicked.connect(self.newEntry)
        self.deleteButton = QtWidgets.QPushButton("Borrar Entrada", self.formGroupBox)
        self.formLayout.addWidget(self.deleteButton)
        self.deleteButton.clicked.connect(self.deleteEntry)

        self.gridLayout.addWidget(self.formGroupBox, 1, 0, 1, 1)

        # Widget Tabla
        self.tableWidget = QtWidgets.QTableWidget(self.centralWidget)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 250))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 1, 10, 1)

        # Dibujo Punto
        self.actionPoint = QtWidgets.QAction("Punto de Red", MainWindow)
        self.actionPoint.setCheckable(True)
        self.actionPoint.triggered.connect(self.point)
        self.menuNuevo.addAction(self.actionPoint)
        self.toolPoint = PointMapTool(self.mapCanvas)
        self.toolPoint.setAction(self.actionPoint)

        # Dibujo de Linea
        self.actionPoly = QtWidgets.QAction("Sendero", MainWindow)
        self.actionPoly.setCheckable(True)
        self.actionPoly.triggered.connect(self.poly)
        self.menuNuevo.addAction(self.actionPoly)
        self.toolPoly = PolyMapTool(self.mapCanvas)
        self.toolPoly.setAction(self.actionPoly)

    def point(self):
        if self.actionPoint.isChecked():
            self.mapCanvas.setMapTool(self.toolPoint)
        else:
            self.mapCanvas.unsetMapTool(self.toolPoint)

    def poly(self):
        if self.actionPoly.isChecked():
            self.mapCanvas.setMapTool(self.toolPoly)
        else:
            self.mapCanvas.unsetMapTool(self.toolPoly)
    """
        Función para la carga de las capas en el mapa 
    """
    def loadMap(self):

        self.conn = psycopg2.connect(dbname='senderosV1', host='localhost', port='5433',
                                     user='postgres', password='root', )
        cur = self.conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' "
                    "AND table_type='BASE TABLE';")
        names = cur.fetchall()

        uri = QgsDataSourceUri()
        uri.setConnection("localhost", "5433", "senderosV1", "postgres", "root")

        layers = []
        i = 0

        # Carga de las capas de la base de datos
        for name in names:
            if name[0] == "spatial_ref_sys" or name[0] == "pointcloud_formats":  # Salto de las tablas de conf. de Postgis
                continue
            uri.setDataSource("public", name[0], "geom")
            layer = QgsVectorLayer(uri.uri(), name[0], 'postgres')
            layers.append(layer)

            if not layers[i].isValid():
                self.showDialog("Error de carga", "Capa " + name[0] + " no se ha cargado", 0)
            else:
                QgsProject.instance().addMapLayer(layers[i])
            i = i + 1

        # Carga de la capa base Plana
        flat_basemap_layer = QgsVectorLayer("./Basemap/GranCanariaMap.shp", "BaseMapFlat")
        if not flat_basemap_layer.isValid():
            self.showDialog("Error de carga", "BaseMapFlat no se ha cargado", 0)
        else:
            flat_basemap_layer.renderer().symbol().setColor(QColor("lightGray"))
            QgsProject.instance().addMapLayer(flat_basemap_layer)
            layers.append(flat_basemap_layer)

        # Carga de la capa base Mapa
        url = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG4326'
        basemap_layer = QgsRasterLayer(url, 'OpenStreetMap', 'wms')
        if not basemap_layer.isValid():
            self.showDialog("Error de carga", "OpenStreetMap no se ha cargado", 0)
        else:
            QgsProject.instance().addMapLayer(basemap_layer)
            layers.append(basemap_layer)

        self.mapCanvas.setLayers(layers)  # Carga de las capas en el mapa
        self.mapCanvas.setExtent(flat_basemap_layer.extent())  # Zoom a la capa base


    """
        Función para determinar si una capa se muestra en el mapa o no
    """

    def showLayer(self, item):
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.name() == "OpenStreetMap":
                continue
            if layer.name() == item.data(0):
                if item.checkState() == 0:  # Item is NOT Check
                    layer.setOpacity(100)
                    item.setCheckState(2)
                elif item.checkState() == 2:  # Item is Check
                    layer.setOpacity(0)
                    item.setCheckState(0)
                self.mapCanvas.refresh()
                return

    """
        Función para el borrado de una tabla completa
    """
    def deleteTable(self):
        item = self.listWidget.currentItem()
        if item.data(0) == "BaseMapFlat" or item.data(0) == "OpenStreetMap":  # Evita las capas no pertenecientes a BD
            self.showDialog("Error de borrado", "Tabla no seleccionada", 0)
            return
        else:
            retval = self.showDialog("Mensaje de confirmación", "¿Seguro que quiere borrar esta Tabla?", 2)
            if retval == 1024:  # Aceptación
                cur = self.conn.cursor()
                query = sql.SQL("DROP TABLE {table}").format(
                    table=sql.Identifier(item.data(0)))
                cur.execute(query)
                self.conn.commit()
                self.listWidget.removeItemWidget(item)
                self.listWidget.update()
                self.showDialog("Resultado de borrar Tabla", "Tabla borrada", 3)
            elif retval == 4194304:  # Cancelación
                return

    """
         Función que carga la tabla con los datos de la base de datos
    """
    def loadTable(self, item):
        if item.data(0) == "BaseMapFlat" or item.data(0) == "OpenStreetMap":  # Evita las capas no pertenecientes a BD
            self.showDialog("Atencion", "Tabla no seleccionada", 0)
            return

        cur = self.conn.cursor()
        cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = %s
                """, [item.data(0)])

        self.column_names = [row[0] for row in cur]
        self.tableWidget.setColumnCount(len(self.column_names))
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)

        try:
            cur.execute(
                sql.SQL("SELECT * FROM {} ORDER BY id ASC").format(sql.Identifier(item.data(0))))
        except Exception:
            self.showDialog("Capa no Valida", "Error de carga", 1)
            return

        data = cur.fetchall()
        self.tableWidget.setRowCount(len(data))

        for row_number, row_data in enumerate(data):
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.update()

    """
        Función que borra una entrada en la base de datos
    """
    def deleteEntry(self):
        row = self.tableWidget.currentRow()
        layer = self.listWidget.currentItem()
        if row == -1 or layer.data(0) == "BaseMapFlat" or layer.data(0) == "OpenStreetMap": # Evita las capas no pertenecientes a BD
            self.showDialog("Error de borrado", "Fila no seleccionada", 0)
            return
        else:
            retval = self.showDialog("Mensaje de confirmación", "¿Seguro que quiere borrar esta fila?", 2)
            if retval == 1024:  # Aceptación
                cur = self.conn.cursor()
                query = sql.SQL("DELETE FROM {table} WHERE id = %s ").format(
                    table=sql.Identifier(layer.data(0)))

                cur.execute(query, [self.tableWidget.item(row, 0).data(0)])

                self.conn.commit()
                self.loadTable(self.listWidget.currentItem())
            elif retval == 4194304:  # Cancelación
                return

    """
        Función que guarda los cambios realizados en una celda de tabla
    """
    def saveTable(self):
        layer = self.listWidget.currentItem()
        itemSelected = self.tableWidget.selectedItems()
        if len(itemSelected) == 0 or layer.data(0) == "BaseMapFlat" or layer.data(0) == "OpenStreetMap": # Evita las capas no pertenecientes a BD
            self.showDialog("Error de guardado", "Dato no seleccionada", 0)
            return

        id = self.tableWidget.item(itemSelected[0].row(), 0)
        column = self.column_names[itemSelected[0].column()]

        cur = self.conn.cursor()
        query = sql.SQL("UPDATE {table} SET {column}= %s WHERE id = %s ").format(
            table=sql.Identifier(layer.data(0)),
            column=sql.Identifier(column))
        entry = itemSelected[0].data(0)
        cur.execute(query, [entry, id.data(0)])

        self.conn.commit()
        self.showDialog("Confirmación", "Cambios guardados", 3)
        self.loadTable(self.listWidget.currentItem())

    """
        Función para crear y mostrar la ventana de creación de tablas
    """
    def showNewTable(self):
        self.newtable = createTableWindow(self.conn)
        self.newtable.show()

    """
        Función que crea y muestra la ventana de creación de entrada de datos
    """

    def newEntry(self):
        layer = self.listWidget.currentItem()
        # Evita las capas no pertenecientes a BD y evita introduir entrada en tabla no cargado
        if layer.data(0) == "BaseMapFlat" or layer.data(0) == "OpenStreetMap"\
                or self.tableWidget.columnCount() == 0 or self.tableWidget.rowCount() == 0:
            self.showDialog("Atencion", "Tabla no seleccionada", 0)
        else:
            self.newDatos = showDatos(self.conn, layer.data(0), self.tableWidget.columnCount(), self.tableWidget.rowCount())
            self.newDatos.show()

    """
        Función para crear y mostrar mensajes de aviso
    """
    def showDialog(self, txtTitle, txtText, icon):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(txtTitle)
        msgBox.setText(txtText)
        if icon == 0:
            msgBox.setIcon(QMessageBox.Warning)
        elif icon == 1:
            msgBox.setIcon(QMessageBox.Critical)
        elif icon == 2:
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        elif icon == 3:
            msgBox.setIcon(QMessageBox.Information)
        ret = msgBox.exec()
        return ret

class PointMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.point = None

    def canvasPressEvent(self, event):
        self.point = self.toMapCoordinates(event.pos())
        vm = QgsVertexMarker(self.canvas)
        vm.setCenter(self.point)
        vm.setColor(QColor(0, 0, 255))
        vm.setIconSize(5)
        vm.setIconType(QgsVertexMarker.ICON_X)
        vm.setPenWidth(3)
        print(self.point.x(), self.point.y())

class PolyMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberband = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rubberband.setColor(Qt.red)
        self.rubberband.setWidth(1)
        self.point = None
        self.points = []

    def canvasPressEvent(self, event):
        self.point = self.toMapCoordinates(event.pos())
        vm = QgsVertexMarker(self.canvas)
        vm.setCenter(self.point)
        vm.setColor(QColor(255, 0, 0))
        vm.setIconSize(5)
        vm.setIconType(QgsVertexMarker.ICON_X)
        vm.setPenWidth(3)
        self.points.append(self.point)
        self.isEmittingPoint = True
        self.showPoly()

    def showPoly(self):
        self.rubberband.reset(QgsWkbTypes.LineGeometry)
        for point in self.points[:-1]:
            self.rubberband.addPoint(point, True)
            self.rubberband.show()
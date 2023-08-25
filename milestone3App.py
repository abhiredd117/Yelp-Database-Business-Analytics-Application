import sys
import psycopg2
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap

qtCreatorFile = "milestone3App.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class myApp(QMainWindow):

    def __init__(self):
        super(myApp, self).__init__()
        self.search = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcodeList.itemSelectionChanged.connect(self.zipcodeChanged)
        self.ui.businessTableCategory.itemSelectionChanged.connect(self.businessCategoryChanged)
        self.ui.clearButton.clicked.connect(self.clearButtonClicked)
        self.ui.searchButton.clicked.connect(self.searchButtonClicked)
        self.ui.refreshButton.clicked.connect(self.refreshButtonClicked)

    def executeQuery(self, sql_str):
        try:
            conn = psycopg2.connect("dbname='milestone3db' user='postgres' host='localhost' password='1234'")
            cur = conn.cursor()
            cur.execute(sql_str)
            conn.commit()
            result = cur.fetchall()
            conn.close()
        except:
            print('Unable to connect!')
        return result
    def loadStateList(self):
        self.ui.stateList.clear()
        sql_str = "SELECT distinct state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList.addItem(row[0])
        except:
            print("Query failed!")
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()
    def stateChanged(self):
        self.clearButtonClicked()
        self.ui.cityList.clear()
        self.ui.zipcodeList.clear()
        self.ui.businessTableDetails.clear()
        self.ui.businessTableCategory.clear()
        state = self.ui.stateList.currentText()
        if (self.ui.stateList.currentIndex() >= 0):
            sql_str = "SELECT distinct city FROM business WHERE state ='" + state + "' ORDER BY city;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.cityList.addItem(row[0])
            except:
                print("Query failed!")
    def cityChanged(self):
        self.ui.zipcodeList.clear()
        self.ui.businessTableCategory.clear()
        self.ui.NumberOfBusiness.clear()
        self.ui.TotalPopulation.clear()
        self.ui.AverageIncome.clear()
        self.ui.topCategories.clear()
        self.ui.businessTableDetails.clear()
        self.ui.businessTableCategory.clear()
        self.ui.businessTableDetails.clear()
        self.ui.topCategories.clear()
        if ((self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0)):
            self.ui.zipcodeList.clear()
            self.ui.businessTableCategory.clear()
            self.ui.businessTableDetails.clear()
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            sql_str = "SELECT distinct postal_code FROM business WHERE state ='" + state + "' AND city = '" + city + "' ORDER BY postal_code;"
            results = self.executeQuery(sql_str)
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.zipcodeList.addItem(row[0])
            except:
                print("Query failed!")
    def zipcodeChanged(self):
        self.ui.businessTableCategory.clear()
        self.ui.topCategories.clear()
        self.ui.businessTableDetails.clear()
        self.search = 0
        self.ui.businessTableDetails.setHorizontalHeaderLabels(
            ['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', '# Checkins'])
        if ((self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0) and (
                len(self.ui.zipcodeList.selectedItems()) > 0)):
            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()
            zipcode = self.ui.zipcodeList.selectedItems()[0].text()

            # POPULATE CATEGORIES
            sql_str = "SELECT DISTINCT bc.category_name FROM Business b INNER JOIN BusinessCategories bc ON b.business_id = bc.business_id WHERE b.postal_code = '{}' ORDER BY bc.category_name;".format(
                zipcode)
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.businessTableCategory.addItem(row[0])
            except Exception as e:
                print(str(e))

            # POPULATE NUMBER OF BUSINESS
            sql_str = "SELECT COUNT(*) AS noBusinesses FROM public.business WHERE postal_code = '{}';".format(
                zipcode)
            try:
                result = self.executeQuery(sql_str)
                self.ui.NumberOfBusiness.setText(str(result[0][0]))
            except Exception as e:
                print(str(e))

            # POPULATE POPULATION
            sql_str = "SELECT population FROM public.zipcodedata where zipcode = '{}'".format(
                zipcode)
            try:
                result = self.executeQuery(sql_str)
                self.ui.TotalPopulation.setText(str(result[0][0]))
            except Exception as e:
                print(str(e))

            # POPULATE MEAN INCOME
            sql_str = "SELECT meanincome FROM public.zipcodedata where zipcode = '{}'".format(
                zipcode)
            try:
                result = self.executeQuery(sql_str)
                self.ui.AverageIncome.setText(str(result[0][0]))
            except Exception as e:
                print(str(e))

            sql_str = "SELECT count(BC.category_name),BC.category_name as countc FROM public.business AS BS JOIN public.businesscategories AS BC ON BS.business_id = BC.business_id WHERE BS.postal_code = '{}' GROUP BY category_name ORDER BY count DESC;".format(
                zipcode)
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #000000;}"
                self.ui.topCategories.horizontalHeader().setStyleSheet(style)
                self.ui.topCategories.setColumnCount(len(results[0]))
                self.ui.topCategories.setRowCount(len(results))
                self.ui.topCategories.setHorizontalHeaderLabels(['#Business', 'Category'])
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.topCategories.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1

            except Exception as e:
                print(str(e))
    def businessCategoryChanged(self):
        self.ui.businessTableDetails.clear()
        self.search = 1
        if ((len(self.ui.businessTableCategory.selectedItems()) > 0) and (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0) and len(self.ui.zipcodeList) > 0 and len(self.ui.zipcodeList.selectedItems()) > 0 and self.search == 1):
            zipcode = self.ui.zipcodeList.selectedItems()[0].text()
            businessCategory = self.ui.businessTableCategory.selectedItems()[0].text()
            sql_str = "SELECT name,address,city,stars,reviewcount,ROUND(reviewrating),numcheckins  FROM public.business AS BS JOIN public.businesscategories AS BC ON BS.business_id = BC.business_id WHERE BS.postal_code = '{}' AND BC.category_name = '{}'".format(zipcode,businessCategory)
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #000000;}"
                self.ui.businessTableDetails.horizontalHeader().setStyleSheet(style)
                self.ui.businessTableDetails.setColumnCount(len(results[0]))
                self.ui.businessTableDetails.setRowCount(len(results))
                self.ui.businessTableDetails.setHorizontalHeaderLabels(
                    ['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', '# Checkins'])
                self.ui.businessTableDetails.resizeColumnsToContents()
                self.ui.businessTableDetails.setColumnWidth(0, 170)
                self.ui.businessTableDetails.setColumnWidth(1, 170)
                self.ui.businessTableDetails.setColumnWidth(2, 100)
                self.ui.businessTableDetails.setColumnWidth(3, 40)
                self.ui.businessTableDetails.setColumnWidth(4, 100)
                self.ui.businessTableDetails.setColumnWidth(5, 100)
                self.ui.businessTableDetails.setColumnWidth(6, 100)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.businessTableDetails.setItem(currentRowCount, colCount,
                                                             QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1

            except Exception as e:
                print(str(e))
    def clearButtonClicked(self):
        self.ui.cityList.clear()
        self.ui.zipcodeList.clear()
        self.ui.NumberOfBusiness.clear()
        self.ui.TotalPopulation.clear()
        self.ui.AverageIncome.clear()
        self.ui.businessTableCategory.clear()
        self.ui.topCategories.clear()
        self.ui.businessTableDetails.clear()
        self.ui.popularBusinessTable.clear()
        self.ui.sucessfulBusiness.clear()
        self.ui.businessTableDetails.setHorizontalHeaderLabels(
            ['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', '# Checkins'])
        self.ui.topCategories.setHorizontalHeaderLabels(['#Business', 'Category'])
        self.ui.sucessfulBusiness.setHorizontalHeaderLabels(
            ['Business Name', 'Review Count', '# Checkins'])
        self.ui.popularBusinessTable.setHorizontalHeaderLabels(
            ['Business Name', 'Stars', 'Review Rating'])
        self.search = 0
    def searchButtonClicked(self):
        if (len(self.ui.zipcodeList) > 0 and len(self.ui.zipcodeList.selectedItems()) > 0):
            self.search = 1
            zipcode = self.ui.zipcodeList.selectedItems()[0].text()
            sql_str = "SELECT name,address,city,stars,reviewcount,ROUND(reviewrating),numcheckins FROM public.business WHERE postal_code = '{}'".format(
                zipcode)
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #000000;}"
                self.ui.businessTableDetails.horizontalHeader().setStyleSheet(style)
                self.ui.businessTableDetails.setColumnCount(len(results[0]))
                self.ui.businessTableDetails.setRowCount(len(results))
                self.ui.businessTableDetails.setHorizontalHeaderLabels(
                    ['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', '# Checkins'])
                self.ui.businessTableDetails.resizeColumnsToContents()
                self.ui.businessTableDetails.setColumnWidth(0, 170)
                self.ui.businessTableDetails.setColumnWidth(1, 170)
                self.ui.businessTableDetails.setColumnWidth(2, 100)
                self.ui.businessTableDetails.setColumnWidth(3, 40)
                self.ui.businessTableDetails.setColumnWidth(4, 100)
                self.ui.businessTableDetails.setColumnWidth(5, 100)
                self.ui.businessTableDetails.setColumnWidth(6, 100)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.businessTableDetails.setItem(currentRowCount, colCount,
                                                             QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1

            except Exception as e:
                print(str(e))

    def refreshButtonClicked(self):
        if (len(self.ui.zipcodeList) > 0 and len(self.ui.zipcodeList.selectedItems()) > 0):

            # Popular Business
            zipcode = self.ui.zipcodeList.selectedItems()[0].text()
            sql_str = "SELECT name,stars,ROUND(reviewrating) FROM public.business WHERE postal_code = '{}' AND stars >=4 ORDER BY stars desc,reviewrating desc".format(
                zipcode)
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #000000;}"
                self.ui.popularBusinessTable.horizontalHeader().setStyleSheet(style)
                self.ui.popularBusinessTable.setColumnCount(len(results[0]))
                self.ui.popularBusinessTable.setRowCount(len(results))
                self.ui.popularBusinessTable.setHorizontalHeaderLabels(
                    ['Business Name', 'Stars', 'Review Rating'])
                self.ui.popularBusinessTable.resizeColumnsToContents()
                self.ui.popularBusinessTable.setColumnWidth(0, 250)
                self.ui.popularBusinessTable.setColumnWidth(1, 100)
                self.ui.popularBusinessTable.setColumnWidth(2, 100)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.popularBusinessTable.setItem(currentRowCount, colCount,
                                                             QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1

            except Exception as e:
                print(str(e))


            # Sucessful Business
            sql_str = "	SELECT name,reviewcount,numcheckins FROM public.business WHERE postal_code = '{}' AND numcheckins >=100 ORDER BY reviewcount desc,numcheckins desc".format(
                zipcode)
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #000000;}"
                self.ui.sucessfulBusiness.horizontalHeader().setStyleSheet(style)
                self.ui.sucessfulBusiness.setColumnCount(len(results[0]))
                self.ui.sucessfulBusiness.setRowCount(len(results))
                self.ui.sucessfulBusiness.setHorizontalHeaderLabels(
                    ['Business Name', 'Review Count', '# Checkins'])
                self.ui.sucessfulBusiness.resizeColumnsToContents()
                self.ui.sucessfulBusiness.setColumnWidth(0, 250)
                self.ui.sucessfulBusiness.setColumnWidth(1, 100)
                self.ui.sucessfulBusiness.setColumnWidth(2, 100)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.sucessfulBusiness.setItem(currentRowCount, colCount,
                                                             QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1

            except Exception as e:
                print(str(e))

    def getBusinessNames(self):
        self.ui.businesses.clear()
        businessname = self.ui.bname.text()
        sql_str = "SELECT name FROM business WHERE name LIKE '%" + businessname + "%' ORDER BY name;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.businesses.addItem(row[0])
        except:
            print("Query failed!")

    def displayBusinessCity(self):
        businessname = self.ui.businesses.selectedItems()[0].text()
        sql_str = "SELECT city FROM business WHERE name = '" + businessname + "';"
        try:
            results = self.executeQuery(sql_str)
            self.ui.bcity.setText(results[0][0])
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myApp()
    window.show()
    sys.exit(app.exec_())

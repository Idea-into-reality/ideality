from PySide6.QtWidgets import (QApplication, QStyle, QMainWindow, QFileSystemModel, QTreeView, QListView, 
                               QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QFileDialog, QToolBar, QFileIconProvider, QMenu, QLineEdit)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDesktopServices, QAction
from PySide6.QtCore import QDir, Qt, Slot, QFileInfo, QModelIndex, QUrl
import os, json


class FolderWindow(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()

        # 윈도우 설정
        self.setWindowTitle(f"{folder_path}")
        self.setGeometry(500, 150, 400, 400)

        # 현재 폴더 경로와 이전/다음 폴더 경로들을 추적하기 위한 리스트와 인덱스
        self.paths = [folder_path]
        self.current_path_index = 0

        # 파일 시스템 리스트 뷰 설정
        self.list_file_system_model = QFileSystemModel()
        self.list_file_system_model.setRootPath(folder_path)
        self.list_view = QListView(self)
        self.list_view.setModel(self.list_file_system_model)
        self.list_view.setRootIndex(self.list_file_system_model.index(folder_path))

        # 윈도우의 중앙 위젯으로 리스트 뷰 설정
        self.setCentralWidget(self.list_view)

        # list_view의 doubleClicked 신호 연결
        self.list_view.doubleClicked.connect(self.open_file)

        # 도구 모음 및 액션 설정
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)
        
        # 아이콘 가져오기
        icon_back = window.style().standardIcon(QStyle.SP_ArrowBack)
        icon_forward = window.style().standardIcon(QStyle.SP_ArrowForward)
        icon_up = window.style().standardIcon(QStyle.SP_ArrowUp)


        self.back_action = QAction(icon_back, "뒤로", self)
        self.back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(self.back_action)
        
        self.forward_action = QAction(icon_forward, "앞으로", self)
        self.forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(self.forward_action)
        
        self.up_action = QAction(icon_up, "상위 폴더", self)
        self.up_action.triggered.connect(self.go_up)
        self.toolbar.addAction(self.up_action)
        
    @Slot(QModelIndex)
    def open_file(self, index):
        file_path = self.list_file_system_model.filePath(index)
        file_info = QFileInfo(file_path)

        if file_info.isDir():
            self.change_directory(file_path)
        elif file_info.isFile():
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def change_directory(self, path):
        # 경로를 변경하고 리스트 및 인덱스를 업데이트
        self.paths = self.paths[:self.current_path_index+1]
        self.paths.append(path)
        self.current_path_index += 1
        
        self.list_view.setRootIndex(self.list_file_system_model.index(path))
        self.setWindowTitle(f"{path}")

    def go_back(self):
        if self.current_path_index > 0:
            self.current_path_index -= 1
            path = self.paths[self.current_path_index]
            self.list_view.setRootIndex(self.list_file_system_model.index(path))
            self.setWindowTitle(f"{path}")

    def go_forward(self):
        if self.current_path_index < len(self.paths) - 1:
            self.current_path_index += 1
            path = self.paths[self.current_path_index]
            self.list_view.setRootIndex(self.list_file_system_model.index(path))
            self.setWindowTitle(f"{path}")

    def go_up(self):
        current_path = self.paths[self.current_path_index]
        parent_path = QFileInfo(current_path).dir().absolutePath()
        
        if parent_path != current_path:
            self.change_directory(parent_path)
            

class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.open_windows = []
        
        # 현재 폴더 경로와 이전/다음 폴더 경로들을 추적하기 위한 리스트와 인덱스
        self.paths= []
        self.current_path_index = -1

        # 도구 모음 및 액션 설정
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)
        # 아이콘 가져오기
        icon_back = self.style().standardIcon(QStyle.SP_ArrowBack)
        icon_forward = self.style().standardIcon(QStyle.SP_ArrowForward)
        icon_up = self.style().standardIcon(QStyle.SP_ArrowUp)

        self.back_action = QAction(icon_back, "뒤로", self)
        self.back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(self.back_action)
        
        self.forward_action = QAction(icon_forward, "앞으로", self)
        self.forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(self.forward_action)
        
        self.up_action = QAction(icon_up, "상위 폴더", self)
        self.up_action.triggered.connect(self.go_up)
        self.toolbar.addAction(self.up_action)
        
        # 윈도우 설정
        self.setWindowTitle("File Explorer")
        self.setGeometry(300, 100, 800, 600)

        # 아이콘 제공자 설정
        self.icon_provider = QFileIconProvider()

        # 즐겨찾기 모델 설정
        self.favorites_model = QStandardItemModel()
        
        self.favorites_root = QStandardItem(self.icon_provider.icon(QFileIconProvider.Folder), "Favorites")
        self.favorites_root.setFlags(self.favorites_root.flags() & ~Qt.ItemIsEditable)
        self.favorites_model.appendRow(self.favorites_root)
        
        self.favorite_folders = QStandardItem(self.icon_provider.icon(QFileIconProvider.Folder), "폴더")
        self.favorite_folders.setFlags(self.favorite_folders.flags() & ~Qt.ItemIsEditable)
        self.favorites_root.appendRow(self.favorite_folders)
        
        self.favorite_files = QStandardItem(self.icon_provider.icon(QFileIconProvider.File), "파일")
        self.favorite_files.setFlags(self.favorite_files.flags() & ~Qt.ItemIsEditable)
        self.favorites_root.appendRow(self.favorite_files)

        # 즐겨찾기 트리 뷰 설정
        self.favorites_view = QTreeView(self)
        self.favorites_view.setModel(self.favorites_model)
        self.favorites_view.header().hide()
        self.favorites_view.clicked.connect(self.on_favorites_clicked)
        self.favorites_view.doubleClicked.connect(self.open_favorite)

        # 파일 시스템 트리 뷰 설정
        self.tree_file_system_model = QFileSystemModel()
        self.tree_file_system_model.setRootPath(QDir.rootPath())
        self.tree_file_system_model.setFilter(QDir.NoDotAndDotDot | QDir.Dirs)

        # 경로를 입력할 QLineEdit 위젯
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText("Enter path for the tree view...")
        self.path_edit.returnPressed.connect(self.on_path_edited)

        self.tree = QTreeView(self)
        self.tree.setModel(self.tree_file_system_model)
        self.tree.setRootIndex(self.tree_file_system_model.index(QDir.rootPath()))
        self.tree.clicked.connect(self.on_tree_clicked)
        
        # 헤더 숨기기
        self.tree.header().hide()
       
        # 이름을 제외한 나머지 열을 숨깁니다.
        for column in range(1, self.tree_file_system_model.columnCount()):
            self.tree.setColumnHidden(column, True)

        # 리스트 뷰 설정
        self.list_file_system_model = QFileSystemModel()
        self.list_file_system_model.setRootPath(QDir.rootPath())
        self.list_view = QListView(self)
        self.list_view.setModel(self.list_file_system_model)

         # list_view의 doubleClicked 신호 연결
        self.list_view.doubleClicked.connect(self.open_file)

        # 경로를 입력할 QLineEdit 위젯
        self.tree_path_edit = QLineEdit(self)
        self.tree_path_edit.setPlaceholderText("Enter path for the tree view...")
        self.tree_path_edit.returnPressed.connect(self.on_tree_path_edited)

        # 레이아웃 설정
        layout = QVBoxLayout()

        # 왼쪽 레이아웃에 QLineEdit과 트리 뷰 추가
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.favorites_view)
        left_layout.addWidget(self.tree_path_edit)
        left_layout.addWidget(self.tree)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.path_edit)
        right_layout.addWidget(self.list_view)
 
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        # layout.addWidget(self.path_edit)  # 기존의 QLineEdit
        layout.addLayout(main_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
       
        fixed_width = 200  # 예시로 200픽셀의 폭을 고정

        self.favorites_view.setFixedWidth(fixed_width)
        self.tree_path_edit.setFixedWidth(fixed_width)
        self.tree.setFixedWidth(fixed_width)

        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)
        self.list_view.selectionModel().selectionChanged.connect(self.on_list_selection_changed)


        # 즐겨찾기 로드
        self.load_favorites()

    @Slot()
    def on_tree_selection_changed(self):
        # 트리의 선택이 변경될 때 리스트 뷰의 선택을 해제합니다.
        self.list_view.clearSelection()

    @Slot()
    def on_list_selection_changed(self):
        # 리스트 뷰의 선택이 변경될 때 트리의 선택을 해제합니다.
        self.tree.clearSelection()

    def change_directory(self, path):
        # 경로를 변경하고 리스트 및 인덱스를 업데이트
        self.paths = self.paths[:self.current_path_index+1]
        
        self.paths.append(path)
        self.current_path_index += 1
        
        self.list_view.setRootIndex(self.list_file_system_model.index(path))
        
    def go_back(self):
        if self.current_path_index > 0:
            self.current_path_index -= 1
            path = self.paths[self.current_path_index]
            self.list_view.setRootIndex(self.list_file_system_model.index(path))
            self.path_edit.setText(path) 
            
    def go_forward(self):
        if self.current_path_index < len(self.paths) - 1:
            self.current_path_index += 1
            path = self.paths[self.current_path_index]
            self.list_view.setRootIndex(self.list_file_system_model.index(path))
            self.path_edit.setText(path) 
            

    def go_up(self, index):
        if self.paths != []:
            current_path = self.paths[self.current_path_index]
            parent_path = QFileInfo(current_path).dir().absolutePath()
            if parent_path != current_path:
                self.list_view.setRootIndex(self.list_file_system_model.index(parent_path))
                self.path_edit.setText(parent_path)   
                self.change_directory(parent_path)
    @Slot()
    def on_tree_path_edited(self):
        """트리 뷰의 루트 경로를 변경하는 슬롯"""
        tree_path = self.tree_path_edit.text()
        if QDir(tree_path).exists():
            self.tree.setRootIndex(self.tree_file_system_model.index(tree_path))

    @Slot(QModelIndex)
    def on_tree_clicked(self, index):
        clicked_path = self.tree_file_system_model.filePath(index)
        if QDir(clicked_path).exists():
            self.list_view.setRootIndex(self.list_file_system_model.index(clicked_path))
            self.path_edit.setText(clicked_path)    
            self.change_directory(self.path_edit.text())
    @Slot()
    def on_path_edited(self):
        main_path = self.path_edit.text()
        if QDir(main_path).exists():
            self.list_view.setRootIndex(self.list_file_system_model.index(main_path))
            self.change_directory(main_path)

    @Slot(QModelIndex)
    def open_favorite(self, index):
        path = index.data(Qt.UserRole)  # 저장했던 경로 정보를 불러옵니다.
        if path:
            file_info = QFileInfo(path)
            if file_info.isFile():
                # 해당 파일을 기본 응용 프로그램으로 실행
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    
    @Slot(QModelIndex)
    def open_file(self, index):
        file_path = self.list_file_system_model.filePath(index)
        file_info = QFileInfo(file_path)

        if file_info.isDir():
            # 선택된 경로가 폴더인 경우 list_view의 루트 인덱스를 해당 폴더로 설정
            self.list_view.setRootIndex(self.list_file_system_model.index(file_path))
            self.path_edit.setText(file_path)
            self.change_directory(self.path_edit.text())
        elif file_info.isFile():
            # 해당 파일을 기본 응용 프로그램으로 실행
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def closeEvent(self, event):
        self.save_favorites()
        super().closeEvent(event)

    def save_favorites(self):
        filepath = 'favorites.json'
        
        folder_favorites = [self.favorites_model.itemFromIndex(self.favorites_model.index(row, 0, self.favorite_folders.index())).data(Qt.UserRole) 
                            for row in range(self.favorite_folders.rowCount())]
        file_favorites = [self.favorites_model.itemFromIndex(self.favorites_model.index(row, 0, self.favorite_files.index())).data(Qt.UserRole) 
                        for row in range(self.favorite_files.rowCount())]

        with open(filepath, 'w') as file:
            json.dump({"folders": folder_favorites, "files": file_favorites}, file) 

    def load_favorites(self):
        filepath = 'favorites.json'
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
                
                folder_favorites = data.get("folders", [])
                file_favorites = data.get("files", [])
                
                for path in folder_favorites:
                    self.add_favorite_item(path, self.favorite_folders)
                
                for path in file_favorites:
                    self.add_favorite_item(path, self.favorite_files)
               
    @Slot()
    def on_favorites_clicked(self, index):
        path = self.favorites_model.itemFromIndex(index).data(Qt.UserRole)
        if path and QDir(path).exists():
            self.list_view.setRootIndex(self.list_file_system_model.index(path))
            self.path_edit.setText(path)
          
            self.change_directory(self.path_edit.text())

    @Slot()
    def add_to_favorites(self):
        # 트리 뷰에서의 선택을 기본으로 합니다.
        current_index = self.tree.currentIndex()
        path = self.tree_file_system_model.filePath(current_index)
        
        # 만약 파일 리스트 뷰에서 항목이 선택되어 있다면, 해당 선택을 사용합니다.
        if self.list_view.selectionModel().hasSelection():
            current_index = self.list_view.currentIndex()
            path = self.list_file_system_model.filePath(current_index)
        
        if path:
            file_info = QFileInfo(path)
            if file_info.isDir():
                self.add_favorite_item(path, self.favorite_folders)
            else:
                self.add_favorite_item(path, self.favorite_files)
                
    def add_favorite_item(self, path, parent_item):
        folder_name = path.split('/')[-1] if '/' in path else path.split('\\')[-1]
        if not folder_name:
            folder_name = os.path.splitdrive(path)[0]  # 드라이브 이름 가져오기 (e.g., "C:")
        favorite_item = QStandardItem(self.icon_provider.icon(QFileInfo(path)), folder_name)
        favorite_item.setFlags(favorite_item.flags() & ~Qt.ItemIsEditable)
        favorite_item.setData(path, Qt.UserRole)
        parent_item.appendRow(favorite_item)

    def contextMenuEvent(self, event):
        # 파일 시스템 트리 위에서 우클릭되었는지 확인
        if self.tree.viewport().rect().contains(self.tree.mapFromGlobal(event.globalPos())):
            menu = QMenu(self)
            selected_index = self.tree.currentIndex() if self.tree.viewport().rect().contains(self.tree.mapFromGlobal(event.globalPos())) else self.list_view.currentIndex()
            tree_selected_path = self.tree_file_system_model.filePath(selected_index) if self.tree.viewport().rect().contains(self.tree.mapFromGlobal(event.globalPos())) else self.list_file_system_model.filePath(selected_index)
            file_info = QFileInfo(tree_selected_path)

            if file_info.isDir():
                add_action = menu.addAction("폴더 즐겨찾기 추가")
                view_in_new_window_action = menu.addAction("새창에서 보기")
                view_in_new_window_action.triggered.connect(lambda: self.view_in_new_window(tree_selected_path))
            else:
                add_action = menu.addAction("파일 즐겨찾기 추가")
            add_action.triggered.connect(self.add_to_favorites)
            # 메뉴 보여주기
            menu.exec(event.globalPos())

        # 파일 리스트 뷰에서 우클릭되었는지 확인
        elif self.list_view.viewport().rect().contains(self.list_view.mapFromGlobal(event.globalPos())):
            menu = QMenu(self)
            # 현재 선택된 항목의 정보를 가져옵니다.
            list_view_selected_index = self.list_view.currentIndex()
            list_view_selected_path = self.list_file_system_model.filePath(list_view_selected_index)
            file_info = QFileInfo(list_view_selected_path)

            # 파일이면 '파일 즐겨찾기 추가' 메뉴를 표시하고 폴더면 '폴더 즐겨찾기 추가' 메뉴를 표시합니다.
            if file_info.isDir():
                add_action = menu.addAction("폴더 즐겨찾기 추가")
                view_in_new_window_action = menu.addAction("새창에서 보기")
                view_in_new_window_action.triggered.connect(lambda: self.view_in_new_window(list_view_selected_path))
            else:
                add_action = menu.addAction("파일 즐겨찾기 추가")
            add_action.triggered.connect(self.add_to_favorites)

            menu.exec(event.globalPos())

        # 즐겨찾기 트리 위에서 우클릭되었는지 확인
        elif self.favorites_view.viewport().rect().contains(self.favorites_view.mapFromGlobal(event.globalPos())):
            menu = QMenu(self)
            # 즐겨찾기 제거 액션
            remove_action = menu.addAction("즐겨찾기 제거")
            remove_action.triggered.connect(self.remove_from_favorites)

            menu.exec(event.globalPos())

    def view_in_new_window(self, folder_path):
        self.folder_window = FolderWindow(folder_path)
        self.folder_window.show()
        self.open_windows.append(window)

    @Slot()
    def remove_from_favorites(self):
        current_index = self.favorites_view.currentIndex()
        if current_index.isValid() and current_index.parent() != self.favorites_model.indexFromItem(self.favorites_root):
            # 선택한 항목의 부모 항목의 인덱스를 가져와서 항목을 제거
            self.favorites_model.removeRow(current_index.row(), current_index.parent())

if __name__ == '__main__':
    app = QApplication([])
    window = FileExplorer()
    window.show()
    app.exec()

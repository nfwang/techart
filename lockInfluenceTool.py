#########################################################################
# LockInfluenceTool by Nelson Wang (nfwang@gmail.com)
# 
# 01-31-2022
# Maya Skinweights paint tool to be used with ArtPaintSkinWeightsTool
#########################################################################

from PySide2 import QtCore, QtWidgets, QtGui
import maya.cmds as cmds
import maya.mel as mel

LEFTRIGHTMIDDLE = ["Lf","Rt","Cn"]

def getMayaWindow():
    for widget in QtWidgets.QApplication.topLevelWidgets():
        try:
            if widget.objectName() == "MayaWindow":
                return widget
        except:
            pass
    print('"MayaWindow" not found.')
    return None


def LockInfluenceTool():
    
    # create dialog    
    mayaWindow = getMayaWindow()

    dialog = LockInfluenceToolDialog(parent=mayaWindow)

    dialog.setWindowTitle('Lock Influence Tool v0.1')
    dialog.setObjectName('lockInfluenceToolMainWindow')
    dialog.updateSkincluster()
    dialog.show()
    
    
class LockInfluenceToolDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(LockInfluenceToolDialog, self).__init__(parent)

        main_vbox = QtWidgets.QVBoxLayout(self)
        
        # Skincluster info
        skincluster_hbox = QtWidgets.QHBoxLayout(self)
        self.skincluster_label = QtWidgets.QLabel(self)
        self.skincluster_label.setText("Skincluster: ")
        
        self.skinclusterName_label = QtWidgets.QLabel(self)
        self.skinclusterName_label.setText("")
        
        
        self.autoPaint_check = QtWidgets.QCheckBox()
        self.autoPaint_check.setText("Auto Paint")
        self.autoPaint_check.setChecked(True)
        self.autoPaint_check.clicked.connect(self.updateSkincluster)
        
        self.pinSkincluster_btn = QtWidgets.QPushButton()
        self.pinSkincluster_btn.setText("PIN")
        self.pinSkincluster_btn.setMaximumWidth(25)
        self.pinSkincluster_btn.setCheckable(True)
        self.pinSkincluster_btn.setToolTip('Pin current skincluster influences')
        self.pinSkincluster_btn.clicked.connect(self.updateSkincluster)

        self.refresh_btn = QtWidgets.QPushButton()
        self.refresh_btn.setText("REFRESH")
        self.refresh_btn.setMaximumWidth(60)
        self.refresh_btn.setToolTip('Refresh UI')
        self.refresh_btn.clicked.connect(self.updateUI)
        

        skincluster_hbox.addWidget(self.skincluster_label)
        skincluster_hbox.addWidget(self.skinclusterName_label)
        skincluster_hbox.addWidget(self.autoPaint_check)
        skincluster_hbox.addWidget(self.pinSkincluster_btn)
        skincluster_hbox.addWidget(self.refresh_btn)
        
        # Filters
        sidesFilter_hbox = QtWidgets.QHBoxLayout(self)
        self.leftFilter_check = QtWidgets.QCheckBox()
        self.leftFilter_check.setText("L")
        self.leftFilter_check.setChecked(True)
        self.leftFilter_check.clicked.connect(self.updateUI)

        self.middleFilter_check = QtWidgets.QCheckBox()
        self.middleFilter_check.setText("M")
        self.middleFilter_check.setChecked(True)
        self.middleFilter_check.clicked.connect(self.updateUI)

        self.rightFilter_check = QtWidgets.QCheckBox()
        self.rightFilter_check.setText("R")
        self.rightFilter_check.setChecked(False)
        self.rightFilter_check.clicked.connect(self.updateUI)

        self.lockedFilter_check = QtWidgets.QCheckBox()
        self.lockedFilter_check.setText("Unlocked")
        self.lockedFilter_check.setChecked(True)
        self.lockedFilter_check.clicked.connect(self.updateUI)
        
        self.unlockedFilter_check = QtWidgets.QCheckBox()
        self.unlockedFilter_check.setText("Locked")
        self.unlockedFilter_check.setChecked(False)
        self.unlockedFilter_check.clicked.connect(self.updateUI)
        
        sidesFilter_hbox.addWidget(self.leftFilter_check)
        sidesFilter_hbox.addWidget(self.middleFilter_check)
        sidesFilter_hbox.addWidget(self.rightFilter_check)
        sidesFilter_hbox.addWidget(self.lockedFilter_check)
        sidesFilter_hbox.addWidget(self.unlockedFilter_check)
        
        self.influence_list = QtWidgets.QListWidget()
        self.influence_list.setToolTip('List of unlocked influences')
        self.influence_list.currentItemChanged.connect(self.changeInfluence)
        
        # List and Buttons
        mayaSelection_label = QtWidgets.QLabel(self)
        mayaSelection_label.setText("Maya Selection:")
        
        self.isolateWeights_btn = QtWidgets.QPushButton()
        self.isolateWeights_btn.setText("ISOLATE")
        self.isolateWeights_btn.clicked.connect(self.isolateSelectedInfluences)
        self.isolateWeights_btn.setToolTip('Unlock viewport selected and lock remaining influences')

        self.unlockSelected_btn = QtWidgets.QPushButton()
        self.unlockSelected_btn.setText("UNLOCK")
        self.unlockSelected_btn.clicked.connect(self.unlockSelected)
        self.unlockSelected_btn.setToolTip('Unlock maya selected joints')

        self.lockSelected_btn = QtWidgets.QPushButton()
        self.lockSelected_btn.setText("LOCK")
        self.lockSelected_btn.clicked.connect(self.lockSelected)
        self.lockSelected_btn.setToolTip('Lock maya selected joints')


        space_label = QtWidgets.QLabel(self)
        space_label.setText("")

        listSelection_label = QtWidgets.QLabel(self)
        listSelection_label.setText("List Selection:")

        self.unlock_btn = QtWidgets.QPushButton()
        self.unlock_btn.setText("UNLOCK")
        self.unlock_btn.clicked.connect(self.unlock)
        self.unlock_btn.setToolTip('Unlock selected influence in list.')

        self.lock_btn = QtWidgets.QPushButton()
        self.lock_btn.setText("LOCK")
        self.lock_btn.clicked.connect(self.lock)
        self.lock_btn.setToolTip('Lock selected influence in list.')

        self.unlockAll_btn = QtWidgets.QPushButton()
        self.unlockAll_btn.setText("UNLOCK ALL")
        self.unlockAll_btn.clicked.connect(self.unlockAll)
        self.unlockAll_btn.setToolTip('Unlock all skincluster influences')

        self.lockAll_btn = QtWidgets.QPushButton()
        self.lockAll_btn.setText("LOCK ALL")
        self.lockAll_btn.clicked.connect(self.lockAll)
        self.lockAll_btn.setToolTip('Lock all skincluster influences')
        
        
        # Buttons
        buttons_vbox = QtWidgets.QVBoxLayout(self)
        buttons_vbox.setAlignment(QtCore.Qt.AlignBaseline)
        buttons_vbox.addWidget(mayaSelection_label)
        buttons_vbox.addWidget(self.isolateWeights_btn)
        buttons_vbox.addWidget(self.unlockSelected_btn)
        buttons_vbox.addWidget(self.lockSelected_btn)
        
        buttons_vbox.addWidget(space_label)
        buttons_vbox.addWidget(listSelection_label)
        
        buttons_vbox.addWidget(self.lock_btn)
        buttons_vbox.addWidget(self.unlock_btn)
        buttons_vbox.addWidget(self.unlockAll_btn)
        buttons_vbox.addWidget(self.lockAll_btn)
        
        listAndFilter_vbox = QtWidgets.QVBoxLayout(self)
        listAndFilter_vbox.addLayout(sidesFilter_hbox)
        listAndFilter_vbox.addWidget(self.influence_list)
        
        listAndButtons_hbox = QtWidgets.QHBoxLayout(self)
        listAndButtons_hbox.addLayout(buttons_vbox)
        listAndButtons_hbox.addLayout(listAndFilter_vbox)
        
        main_vbox.addLayout(skincluster_hbox)
        main_vbox.addLayout(sidesFilter_hbox)
        main_vbox.addLayout(listAndButtons_hbox)
        
        self.setLayout(main_vbox)

        self.setGeometry(300, 300, 200, 300)
        self.setWindowTitle('QListWidget')

        # initate script job
        self.SCRIPT_JOB_NUMBER = cmds.scriptJob( event= ["SelectionChanged", self.updateSkincluster], protected=True)
        self.skincluster = None
        self.current_item = None
        

    def updateSkincluster(self):
        
        # Get Skincluster from selection
        node = cmds.ls(sl=1, type="transform")
        
        if not node:
            return
        else:
            node = node[0]
        
        skincluster = mel.eval ('findRelatedSkinCluster "{}"'.format(node))
        if not skincluster:
            return 
        
        if not self.pinSkincluster_btn.isChecked():
            self.skincluster = skincluster
            self.skinclusterName_label.setText(skincluster) 
        
        if self.autoPaint_check.checkState():
            cmds.ArtPaintSkinWeightsTool()
            
        self.updateUI()

    def updateUI(self):
        ''' Update the UI '''
        
        if not self.skincluster:
            return
    
        # clear the list if another skincluster is found
        influences = cmds.skinCluster(self.skincluster, query=True, influence=True)
        
        # filter and organize list
        influences.sort()
        
        # filter list
        listCount = 0
        self.influence_list.clear()
        for influence in influences:
            side_filtered = None
            
            # filter for side
            if ( self.leftFilter_check.checkState() ) and (influence.find(LEFTRIGHTMIDDLE[0]) != -1):
                side_filtered = influence
            elif ( self.rightFilter_check.checkState() ) and (influence.find(LEFTRIGHTMIDDLE[1]) != -1):
                side_filtered = influence
            elif ( self.middleFilter_check.checkState() ) and (influence.find(LEFTRIGHTMIDDLE[2]) != -1):
                side_filtered = influence
            
            if not side_filtered:
                continue
            
            # filter for locked state
            if ( self.lockedFilter_check.checkState() ) and (cmds.getAttr(side_filtered+".lockInfluenceWeights") == False):
                self.influence_list.addItem(side_filtered)
                listCount += 1
                
            if ( self.unlockedFilter_check.checkState() ) and (cmds.getAttr(side_filtered+".lockInfluenceWeights") == True):
                self.influence_list.addItem(side_filtered)
                self.influence_list.item(listCount).setForeground(QtCore.Qt.red);
                listCount += 1
        
        # select the item after rebuilding the list
        if self.current_item:
            for ii in range(self.influence_list.count()):
                if self.influence_list.item(ii).text() == self.current_item:
                    self.influence_list.setCurrentRow(ii)
                    break

    def unlockSelected(self):
        for obj in cmds.ls(sl=1):
            cmds.setAttr(obj+ ".lockInfluenceWeights", 0)
            self.current_item = obj

        self.updateUI()

    def lockSelected(self):
        for obj in cmds.ls(sl=1):
            cmds.setAttr(obj+ ".lockInfluenceWeights", 1)
            self.current_item = obj
            
        self.updateUI()

    def unlock(self):
        if not self.skincluster:
            return 
        
        current_influence = self.influence_list.currentItem()
        
        if not current_influence:
            return
            
        cmds.setAttr(current_influence.text() + ".lockInfluenceWeights", 0)

        # set to the next item
        current_row = self.influence_list.currentRow()
        
        self.updateUI()
        if current_row < self.influence_list.count():
            self.influence_list.setCurrentRow(current_row + 1)
        else:
            self.influence_list.setCurrentRow(current_row)


    def lock(self):
        if not self.skincluster:
            return 

        current_influence = self.influence_list.currentItem()

        if not current_influence:
            return

        
        cmds.setAttr(current_influence.text() + ".lockInfluenceWeights", 1)
        
        # set to the next item
        current_row = self.influence_list.currentRow()
        
        if current_row < (self.influence_list.count() - 1):
            current_row += 1
            
        next_item = self.influence_list.item(current_row)
        self.current_item = next_item.text()
        
        self.updateUI()
        
    
    def unlockAll(self):
        if not self.skincluster:
            return 

        influences = cmds.skinCluster(self.skincluster, query=True, influence=True)
        for influence in influences:
            cmds.setAttr(influence+".lockInfluenceWeights", 0)

        self.updateUI()
            

    def lockAll(self):
        if not self.skincluster:
            return 

        influences = cmds.skinCluster(self.skincluster, query=True, influence=True)
        for influence in influences:
            cmds.setAttr(influence+".lockInfluenceWeights", 1)
            
        self.updateUI()
    
    def isolateSelectedInfluences(self):
        
        if not self.skincluster:
            return 
            
        sel = cmds.ls(sl=1)
        influences = cmds.skinCluster(self.skincluster, query=True, influence=True)
        
        for influence in influences:
            if influence in sel:
                cmds.setAttr(influence+".lockInfluenceWeights", 0)
            else:
                cmds.setAttr(influence+".lockInfluenceWeights", 1)

        self.current_item = sel[0]
        self.updateUI()
    
    def changeInfluence(self, current, previous):
        
        influences = cmds.skinCluster(self.skincluster, influence=True, query=True)
    
        ctx = cmds.currentCtx()
        if cmds.contextInfo(ctx, query=True, c=True)=='artAttrSkin':
            if previous:
                mel.eval('artSkinInflListChanging "{}" 0;'.format(previous.text()))
                
            if current:    
                mel.eval('artSkinInflListChanging "{}" 1;'.format(current.text()))
                
            mel.eval('artSkinInflListChanged artAttrSkinPaintCtx;')

    
    def closeEvent( self, event ):
        # Kill the ScriptJob prior to closing the dialog.
        cmds.scriptJob( kill=self.SCRIPT_JOB_NUMBER, force=True )
        super( LockInfluenceToolDialog, self ).closeEvent( event )

LockInfluenceTool()
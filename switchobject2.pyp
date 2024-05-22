"""
Title:
    SwitchObject 2.0.1

Author:
    Frank Willeke

Description:
    Lets you set easily one object out of a group of objects visible, while setting the others invisible.
    Ideal for enabling different variations of objects or scene parts.
"""

import os
import c4d

ID_SWITCHOBJECT2: int = 1063289
PLUGIN_TITLE: str = "SwitchObject 2.0.1"
IDS_SWITCHOBJECT2: str = "SwitchObject"


class SwitchObject2(c4d.plugins.ObjectData):
    def __init__(self, *args):
        self.SetOptimizeCache(False)

    def Init(self, op: c4d.GeListNode, isCloneInit: bool=False) -> bool:
        """
        Initializes default attribute values.
        """
        # Initialize attribute
        self.InitAttr(op, int, c4d.SWITCHOBJECT2_CHILD)
        self.InitAttr(op, c4d.BaseList2D, c4d.SWITCHOBJECT2_PARENTLINK)
        self.InitAttr(op, bool, c4d.SWITCHOBJECT2_RENAME)

        # Set default attribute value
        if not isCloneInit:
            dataRef = op.GetDataInstance()
            dataRef[c4d.SWITCHOBJECT2_CHILD] = 0
            dataRef[c4d.SWITCHOBJECT2_PARENTLINK] = None
            dataRef[c4d.SWITCHOBJECT2_RENAME] = False

        return True

    def AddToExecution(self, op: c4d.BaseObject, list: c4d.plugins.PriorityList) -> bool:
        """
        Adds the object to the document's execution list.
        """
        list.Add(op, c4d.EXECUTIONPRIORITY_EXPRESSION, c4d.EXECUTIONFLAGS_EXPRESSION)
        return True

    def Execute(self, op: c4d.BaseObject, doc: c4d.documents.BaseDocument, bt, priority: int, flags: int) -> int:
        """
        Called when the object is executed.
        """
        # Get object's container
        dataRef: c4d.BaseContainer = op.GetDataInstance()

        # Get desired child index from user
        childIndex = dataRef[c4d.SWITCHOBJECT2_CHILD]

        # Get parent object of group to switch
        parentObject: c4d.BaseObject = dataRef[c4d.SWITCHOBJECT2_PARENTLINK]
        if parentObject is None:
            parentObject = op

        # Iterate child hierarchy
        currentChildObject: c4d.BaseObject = parentObject.GetDown()
        currentChildIndex: int = 0
        anythingChanged: bool = False
        activeObjectName: str = IDS_SWITCHOBJECT2
        while currentChildObject:
            # Determine new object mode
            objectMode: int = -1
            if currentChildIndex == childIndex:
                activeObjectName = IDS_SWITCHOBJECT2 + ": " + currentChildObject.GetName()
                objectMode = c4d.MODE_UNDEF
            else:
                objectMode = c4d.MODE_OFF

            # Get current editor mode, change it if new mode is different
            currentMode: int = currentChildObject.GetEditorMode()
            if currentMode != objectMode:
                currentChildObject.SetEditorMode(objectMode)
                anythingChanged = True

            # Get current render mode, change it if new mode is different
            currentMode = currentChildObject.GetRenderMode()
            if currentMode != objectMode:
                currentChildObject.SetRenderMode(objectMode)
                anythingChanged = True

            # Continue
            currentChildIndex += 1
            currentChildObject = currentChildObject.GetNext()

        # Rename SwitchObject, if desired
        if dataRef[c4d.SWITCHOBJECT2_RENAME]:
            op.SetName(activeObjectName)

        # If anything has been changed, update
        if anythingChanged:
            c4d.EventAdd()

        return c4d.EXECUTIONRESULT_OK

    def GetDDescription(self, node: c4d.GeListNode, description: c4d.Description, flags: int):
        """
        Populates SWITCHOBJECT2_CHILD cycle with names of child objects.
        """
        # Before adding dynamic parameters, load the parameters from the description resource
        if not description.LoadDescription(node.GetType()):
            return False

        # Get description single ID
        singleId: c4d.DescID = description.GetSingleDescID()
        paramId: c4d.DescID = c4d.DescID(c4d.SWITCHOBJECT2_CHILD)

        # Populate SWITCHOBJECT2_CHILD
        if singleId is None or paramId.IsPartOf(singleId)[0]:
            # Get cycle attribute settings container
            descSettings: c4d.BaseContainer = description.GetParameterI(c4d.SWITCHOBJECT2_CHILD)

            # Create container for cycle elements
            cycleElements: c4d.BaseContainer() = c4d.BaseContainer()

            # Get parent object of group to switch
            dataRef: c4d.BaseContainer = node.GetDataInstance()
            parentObject: c4d.BaseObject = dataRef[c4d.SWITCHOBJECT2_PARENTLINK]
            if parentObject is None:
                parentObject = node

            # Get node's first child object
            currentChildObject: c4d.BaseObject = parentObject.GetDown()
            if currentChildObject is None:
                # Add dummy element
                cycleElements.SetString(0, "(None)")
            else:
                # Iterate child hierarchy, populate container
                currentChildIndex: int = 0
                while currentChildObject:
                    # Add entry to cycle container
                    cycleElements.SetString(currentChildIndex, currentChildObject.GetName())

                    # Continue
                    currentChildIndex += 1
                    currentChildObject = currentChildObject.GetNext()

            # Set elements to cycle
            descSettings.SetContainer(c4d.DESC_CYCLE, cycleElements)

        # After parameters have been loaded and added successfully, return True and DESCFLAGS_DESC_LOADED with the input flags
        return (True, flags | c4d.DESCFLAGS_DESC_LOADED)


# Registers object plugin
if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    iconFilename = os.path.join(directory, "res", "oswitchobject2.tif")
    iconBitmap = None

    # Load icon bitmap, if exists
    if os.path.isfile(iconFilename):
        # Creates a BaseBitmap
        iconBitmap = c4d.bitmaps.BaseBitmap()
        if iconBitmap is None:
            raise MemoryError("Failed to create a BaseBitmap.")

        # Init the BaseBitmap with the icon
        if iconBitmap.InitWith(iconFilename)[0] != c4d.IMAGERESULT_OK:
            raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    registerResult: bool = c4d.plugins.RegisterObjectPlugin(id=ID_SWITCHOBJECT2, str=IDS_SWITCHOBJECT2, g=SwitchObject2, description="oswitchobject2", icon=iconBitmap, info=c4d.OBJECT_CALL_ADDEXECUTION)
    print("Registered" if registerResult else "Failed to register", PLUGIN_TITLE)

import os
import random
import xml.dom.minidom
import xml.dom.minidom as minidom
from pathlib import Path
import codecs

import cv2


# from matplotlib import pyplot as plt

class MakeXML:
    def __init__(self, public_ScrewDriver_ROI):
        self.screwdriver_roi = public_ScrewDriver_ROI

    def Create_XML_ForGrab(self, imgName):
        self.XML_Design(imgName)

    def Create_XML_ForImgaes(self, input_file):
        img_filenames = os.listdir(input_file)
        for img_filename in img_filenames:
            # Result = cv2.flip(cv2.imread(fr'{input_file}\{img_filename}', cv2.IMREAD_GRAYSCALE), 1)
            # cv2.imwrite(fr'{output_file}\{img_filename}', Result)
            self.XML_Design(img_filename[:-4])

    def XML_Design(self, imgName):
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
        dom = minidom.getDOMImplementation().createDocument(None, "root", None)
        doc = xml.dom.minidom.Document()
        writeroot = doc.createElement('annotation')
        doc.appendChild(writeroot)
        nodeName = doc.createElement('filename')
        nodeText = doc.createTextNode(imgName)
        nodeName.appendChild(nodeText)
        doc.firstChild.appendChild(nodeName)

        nodeName = doc.createElement('path')
        nodeText = doc.createTextNode(imgName)
        nodeName.appendChild(nodeText)
        doc.firstChild.appendChild(nodeName)

        nodeName = doc.createElement('source')
        nodetext = doc.createTextNode('Unknown')
        node = doc.createElement('database')
        node.appendChild(nodetext)
        nodeName.appendChild(node)
        doc.firstChild.appendChild(nodeName)

        nodeName = doc.createElement('size')
        nodetext = doc.createTextNode(str(3400))
        node = doc.createElement('width')
        node.appendChild(nodetext)
        nodeName.appendChild(node)
        nodetext = doc.createTextNode(str(1852))
        node = doc.createElement('height')
        node.appendChild(nodetext)
        nodeName.appendChild(node)
        nodetext = doc.createTextNode('3')
        node = doc.createElement('depth')
        node.appendChild(nodetext)
        nodeName.appendChild(node)
        doc.firstChild.appendChild(nodeName)

        for i, roi_data in enumerate(self.screwdriver_roi.ROI_List):
            W, H, X, Y = self.Random_label(roi_data)
            xmin = int(X)
            ymin = int(Y)
            xmax = int(X + W)
            ymax = int(Y + H)

            text = roi_data.Type
            print(text, xmax, xmin, ymax, ymin)

            nodeName = doc.createElement('object')

            nodetext = doc.createTextNode(text)
            node = doc.createElement('name')
            node.appendChild(nodetext)
            nodeName.appendChild(node)

            node = doc.createElement('pose')
            nodetext = doc.createTextNode('Unspecified')
            node.appendChild(nodetext)
            nodeName.appendChild(node)

            node = doc.createElement('truncated')
            nodetext = doc.createTextNode('0')
            node.appendChild(nodetext)
            nodeName.appendChild(node)

            node = doc.createElement('difficult')
            nodetext = doc.createTextNode('0')
            node.appendChild(nodetext)
            nodeName.appendChild(node)

            nodeName2 = doc.createElement('bndbox')

            nodeName3_xmin = doc.createElement('xmin')
            nodetext3 = doc.createTextNode(str(xmin))
            nodeName3_xmin.appendChild(nodetext3)
            nodeName2.appendChild(nodeName3_xmin)

            nodeName3_ymin = doc.createElement('ymin')
            nodetext3 = doc.createTextNode(str(ymin))
            nodeName3_ymin.appendChild(nodetext3)
            nodeName2.appendChild(nodeName3_ymin)

            nodeName3_xmax = doc.createElement('xmax')
            nodetext3 = doc.createTextNode(str(xmax))
            nodeName3_xmax.appendChild(nodetext3)
            nodeName2.appendChild(nodeName3_xmax)

            nodeName3_ymax = doc.createElement('ymax')
            nodetext3 = doc.createTextNode(str(ymax))
            nodeName3_ymax.appendChild(nodetext3)
            nodeName2.appendChild(nodeName3_ymax)

            nodeName.appendChild(nodeName2)

            doc.firstChild.appendChild(nodeName)

        fp = codecs.open(rf'./yolo_xml/{imgName}.xml', 'w', "utf-8")
        doc.writexml(fp, indent='\t', newl='\n', addindent='\t')
        fp.close()

    def Random_label(self, roi_data):
        W = random.randint(100, 120)
        H = random.randint(100, 120)
        X = roi_data.X + random.randint(-5, 5)
        Y = roi_data.Y + random.randint(-5, 5)
        return W, H, X, Y





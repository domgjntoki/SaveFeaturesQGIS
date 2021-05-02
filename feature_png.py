from PIL import Image, ImageDraw
from gqis.core import QgsWkbTypes
from math import ceil
import numpy as np


def get_starting_values(bounding):
    # mantém 2 casas de precisão
    w = ceil(bounding.width() * 100)
    h = ceil(bounding.height() * 100)
    im = Image.new("RGBA", (w, h),
                   (255, 255, 255))
    min_x = bounding.xMinimum() * 100
    min_y = bounding.yMinimum() * 100
    return im, min_x, min_y


def convert_coordinates(min_x, min_y, n):
    n = np.round(n, 2)
    n *= 100
    n = np.ceil(n)
    n = n.tolist()
    n = [(x - min_x, y - min_y) for x, y in n]
    n = [tuple(row) for row in n]
    return n


def image_from_point(x, bounding):
    im, min_x, min_y = get_starting_values(bounding)

    draw = ImageDraw.Draw(im)
    n = convert_coordinates(min_x, min_y, np.array(x))
    draw.point(n, fill="00FF00")
    return im


def image_from_multi_point(x, bounding):
    im, min_x, min_y = get_starting_values(bounding)

    draw = ImageDraw.Draw(im)
    for point in x:
        n = convert_coordinates(min_x, min_y, np.array(point))
        draw.point(n, fill="00FF00")
    return im


def image_from_line(x, bounding):
    im, min_x, min_y = get_starting_values(bounding)

    draw = ImageDraw.Draw(im)
    n = np.array(x)
    n = convert_coordinates(min_x, min_y, n)
    draw.line(n, fill="#00FF00", width=25, joint=3)
    return im


def image_from_multi_line(x, bounding):
    im, min_x, min_y = get_starting_values(bounding)

    draw = ImageDraw.Draw(im)
    for line in x:
        n = np.array(line)
        n = convert_coordinates(min_x, min_y, n)
        draw.line(n, fill="#00FF00", width=25, joint=3)
    return im


def image_from_polygon(x, bounding):
    im, min_x, min_y = get_starting_values(bounding)

    draw = ImageDraw.Draw(im)
    for figure in x:
            n = np.array(figure)
            n = convert_coordinates(min_x, min_y, n)
            draw.polygon(n, fill=None, outline="blue")
    return im


def image_from_multipolygon(x, bounding):
    im, min_x, min_y = get_starting_values(bounding)

    draw = ImageDraw.Draw(im)

    for polygon in x:
        for figure in polygon:
            n = np.array(figure)
            n = convert_coordinates(min_x, min_y, n)
            draw.polygon(n, fill=None, outline="blue")
    return im


def feature_to_png(feature) -> Image:
    geom = feature.geometry()
    bounding = geom.boundingBox()
    geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())

    image = None
    if geom.type() == QgsWkbTypes.PointGeometry:
        # the geometry type can be of single or multi type
        if geomSingleType:
            x = geom.asPoint()
            image = image_from_point(x, bounding)
        else:
            x = geom.asMultiPoint()
            image = image_from_multi_point(x, bounding)
    elif geom.type() == QgsWkbTypes.LineGeometry:
        if geomSingleType:
            x = geom.asPolyline()
            image = image_from_line(x, bounding)
        else:
            x = geom.asMultiPolyline()
            image = image_from_multi_line(x, bounding)
    elif geom.type() == QgsWkbTypes.PolygonGeometry:
        if geomSingleType:
            x = geom.asPolygon()
            image = image_from_polygon(x, bounding)
        else:
            x = geom.asMultiPolygon()
            image = image_from_multipolygon(x, bounding)
    else:
        print("Unknown or invalid geometry")

    if image is None:
        return image

    return image


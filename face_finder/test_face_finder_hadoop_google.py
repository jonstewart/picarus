#!/usr/bin/env python
# (C) Copyright 2010 Brandyn A. White
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ =  'Brandyn A. White <bwhite@cs.umd.edu>'
__license__ = 'GPL V3'

import hadoopy
import time

def main():
#    in_path = '/tmp/bwhite/input/1266413011.32-003-fn-data'
#    out_path = '/tmp/bwhite/output/tp/face/run-%f' % time.time()
    in_path = '/user/brandyn/flickr/voc07/flickr_photo_conv4-1297714349.074514'
    out_path = '/user/brandyn/tp/facefinder/run-%f' % time.time()
    hadoopy.launch_frozen(in_path, out_path, 'face_finder.py', reducer=False,
                          files=['haarcascade_frontalface_default.xml'])
main()

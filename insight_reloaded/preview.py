# -*- coding: utf-8 -*-
"""Preview documents"""

import logging
from os import path, chdir, listdir
from shutil import rmtree, copyfile
from tempfile import mkdtemp
try:
    from subprocess import STDOUT, check_output, CalledProcessError
except ImportError:  # check_output new in 2.7, so use a backport for <=2.6
    from subprocess32 import STDOUT, check_output, CalledProcessError


class PreviewException(Exception):
    pass


class DocumentPreview(object):

    def __init__(self, file_obj, callback, sizes, max_previews,
                 base_tmp_folder, storage, crop=False):
        self.file_obj = file_obj
        self.callback = callback
        self.filename = file_obj.name
        self.pages = 1  # sane default
        self.sizes = sizes
        self.max_previews = max_previews
        self.base_tmp_folder = base_tmp_folder
        self.tmp_folder = mkdtemp(dir=self.base_tmp_folder)
        self.storage = storage
        self.crop = crop

    def __unicode__(self):
        return unicode(self.doc_id)

    def create_previews(self):
        """Calls docsplit with the proper parameters."""

        self.storage.prepare()

        chdir(self.tmp_folder)
        preview_folder = path.join(self.tmp_folder, 'previews')
        self.pages = self.get_num_pages()
        if self.pages < self.max_previews:
            self.max_previews = self.pages  # max_previews <= pages
        pages = '1-%s' % self.max_previews
        logging.info(
            "Creating previews in %s for pages '%s'" % (preview_folder, pages))
        cmd = "%(cmd)s -o %(path)s -p %(pages)s -s %(sizes)s -f png %(file)s"
        try:
            check_output(cmd % {'cmd': "docsplit images",
                                'path': preview_folder,
                                'pages': pages,
                                'sizes': ','.join(self.sizes.keys()),
                                'file': self.filename},
                         shell=True,
                         stderr=STDOUT)
        except CalledProcessError, e:
            msg = u"[PREVIEW] Error while previewing %s: %s. Output: %r" % (
                self.filename, e, e.output)
            raise PreviewException(msg)
        # rename each preview using the format 'filename_{size}_p{page}.png'
        # and save all files in the "previews" folder, not in subfolders
        for size_name, size in self.sizes.iteritems():
            folder = path.join(preview_folder, size_name)  # previews/150
            for f in listdir(folder):  # filenames: filename_<page num>.png
                filename_end = f.split('_')[-1]  # <page_num>.png
                page_num = filename_end[:-4]  # remove the '.png' extension
                new_name = 'document_%s_p%s.png' % (size, page_num)
                self.storage.save(path.join(folder, f), new_name)
        if self.crop:
            self.add_crop(self.crop)

    def add_crop(self, crop):
        """Add a cropped version of the first page 'normal' sized preview"""
        logging.info(u"Cropping %s%%" % crop)
        first_page = self.storage.get_path('document_normal_p1.png')
        # copy the "to be cropped" file outside the previews folder: if the
        # crop fails, we don't want to add the full image as a cropped version
        tmp_file = path.join(self.tmp_folder, 'before_cropping.png')
        copyfile(first_page, tmp_file)
        cmd = "gm mogrify -crop 100%%x%s%% %s" % (crop, tmp_file)
        try:
            check_output(cmd, shell=True, stderr=STDOUT)
        except CalledProcessError, e:
            msg = u"[PREVIEW] Error while cropping %s: %s. Output: %r" % (
                tmp_file, e, e.output)
            raise PreviewException(msg)

        self.storage.save(tmp_file, 'document_normal_p1_cropped.ong')

    def get_num_pages(self):
        """Return the number of pages for the document"""
        logging.info(u"Getting num pages for %s" % self.filename)
        cmd = "docsplit length %s" % self.filename
        try:
            output = check_output(cmd, shell=True, stderr=STDOUT)
        except CalledProcessError, e:
            msg = u"[PREVIEW] Failed get %s num pages: %s. Output: %r" % (
                self.filename, e, e.output)
            raise PreviewException(msg)
        num_pages = output.strip()
        if num_pages.isdigit():
            return int(num_pages)
        logging.info(u"Counted %s pages" % output)
        raise PreviewException(u"[PREVIEW] output isn't a number: %s" % output)

    def cleanup(self):
        """Remove the document and its previews"""
        if self.tmp_folder is not None and path.exists(self.tmp_folder):
            logging.info(u"Removing %s" % self.tmp_folder)
            rmtree(self.tmp_folder, ignore_errors=True)

import requests
import os
import io

import openload_exceptions


class CancelledError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__


class BufferReader(io.BytesIO):
    def __init__(self, buf=b'',
                 callback=None,
                 cb_args=(),
                 cb_kwargs={}):
        self._callback = callback
        self._cb_args = cb_args
        self._cb_kwargs = cb_kwargs
        self._progress = 0
        self._len = len(buf)
        io.BytesIO.__init__(self, buf)

    def __len__(self):
        return self._len

    def read(self, n=-1):
        chunk = io.BytesIO.read(self, 1024 * 1024)
        self._progress += int(len(chunk))
        self._cb_kwargs.update({
            'size': self._len,
            'progress': self._progress
        })
        if self._callback:
            try:
                self._callback(*self._cb_args, **self._cb_kwargs)
            except Exception as e:  # catches exception from the callback
                print(e)
                raise CancelledError('The upload was cancelled.')
        return chunk


def progress(size=None, progress=None):
    #print("{0} / {1}".format(size, progress))
    percent = progress * 100 / size
    print("{percent:3.0f}%".format(percent=percent))


class OpenLoad(object):
    api_base_url = 'https://api.openload.co/{api_version}/'
    api_version = 1

    def __init__(self, login_id, login_key):
        """Initializes OpenLoad instance with given parameters and formats api base url.

        Args:
            login_id (str): API Login found in openload.co
            login_key (str): API Key found in openload.co

        Returns:
            None

        """
        self.login_id = login_id
        self.login_key = login_key
        self.api_url = self.api_base_url.format(api_version=self.api_version)

    @classmethod
    def _check_status(cls, response_json):
        """Check the status of the incoming response, raise exception if status is not 200.

        Args:
            response_json (dict): results of the response of the GET request.

        Returns:
           None

        """
        status = response_json['status']
        msg = response_json['msg']

        if status == 400:
            raise openload_exceptions.BadRequestException(msg)
        elif status == 403:
            raise openload_exceptions.PermissionDeniedException(msg)
        elif status == 404:
            raise openload_exceptions.FileNotFoundException(msg)
        elif status == 451:
            raise openload_exceptions.UnavailableForLegalReasonsException(msg)
        elif status == 509:
            raise openload_exceptions.BandwidthUsageExceeded(msg)
        elif status >= 500:
            raise openload_exceptions.ServerErrorException(msg)

    @classmethod
    def _process_response(cls, response_json):
        """Check the incoming response, raise error if it's needed otherwise return the incoming response_json

        Args:
            response_json (dict): results of the response of the GET request.

        Returns:
            dict: results of the response of the GET request.

        """
        cls._check_status(response_json)
        return response_json['result']

    @staticmethod
    def _progress(size, progress):
        """Progress callback

        """
        percent = progress * 100 / size
        print("{percent:3.0f}%".format(percent=percent))

    def _get(self, url, params=None):
        """Used by every other method, it makes a GET request with the given params.

        Args:
            url (str): relative path of a specific service (account_info, ...).
            params (:obj:`dict`, optional): contains parameters to be sent in the GET request.

        Returns:
            dict: results of the response of the GET request.

        """
        if not params:
            params = {}

        params.update({'login': self.login_id, 'key': self.login_key})
        response = requests.get(self.api_url + url, params)
        response_json = response.json()

        return self._process_response(response_json)

    def upload_link(self, folder_id=None, sha1=None, httponly=False):
        """Makes a request to prepare for file upload.

        Note:
            If folder_id is not provided, it will make and upload link to the ``Home`` folder.

        Args:
            folder_id (:obj:`str`, optional): folder-ID to upload to.
            sha1 (:obj:`str`, optional): expected sha1 If sha1 of uploaded file doesn't match this value, upload fails.
            httponly (:obj:`bool`, optional): If this is set to true, use only http upload links.

        Returns:
            dict: dictionary containing (url: will be used in actual upload, valid_until). ::

                {
                    "url": "https://1fiafqj.oloadcdn.net/uls/nZ8H3X9e0AotInbU",
                    "valid_until": "2017-08-19 19:06:46"
                }

        """
        kwargs = {'floder': folder_id, 'sha1': sha1, 'httponly': httponly}
        params = {key: value for key, value in kwargs.items() if value}
        return self._get('file/ul', params=params)

    def upload_file(self, file_path, folder_id=None, sha1=None, httponly=False, progress_cb=None):
        """Calls upload_link request to get valid url, then it makes a post request with given file to be uploaded.
        No need to call upload_link explicitly since upload_file calls it.

        Note:
            If folder_id is not provided, the file will be uploaded to ``Home`` folder.

        Args:
            file_path (str): full path of the file to be uploaded.
            folder_id (:obj:`str`, optional): folder-ID to upload to.
            sha1 (:obj:`str`, optional): expected sha1 If sha1 of uploaded file doesn't match this value, upload fails.
            httponly (:obj:`bool`, optional): If this is set to true, use only http upload links.

        Returns:
            dict: dictionary containing uploaded file info. ::

                {
                    "content_type": "application/zip",
                    "id": "0yiQTPzi4Y4",
                    "name": 'favicons.zip',
                    "sha1": 'f2cb05663563ec1b7e75dbcd5b96d523cb78d80c',
                    "size": '24160',
                    "url": 'https://openload.co/f/0yiQTPzi4Y4/favicons.zip'
                 }

        """
        upload_url_response_json = self.upload_link(
            folder_id=folder_id, sha1=sha1, httponly=httponly)
        upload_url = upload_url_response_json['url']

        files = {"upfile": (os.path.basename(file_path),
                            open(file_path, 'rb').read())}
        (data, ctype) = requests.packages.urllib3.filepost.encode_multipart_formdata(files)
        headers = {
            "Content-Type": ctype
        }

        if not progress_cb:
            progress_cb = self._progress
        body = BufferReader(data, progress_cb)
        try:
            response_json = requests.post(
                upload_url, data=body, headers=headers).json()
        except Exception as e:
            print(e)
            return
        self._check_status(response_json)
        return response_json['result']


g_login_id = '1cc181950882fe13'
g_login_key = 'Ji82gj4k'


def main():
    #file_path = 'test.mp4'
    # Download(file_id)
    #file_path = 'E:\\迅雷下载\\ok\\Marley Brinx480p.mp4'
    file_path = 'G:\\迅雷下载\\如懿传-part\\如懿传.EP61-EP62.Ruyis.Royal.Love.in.the.Palace.2018.1080p.WEB-DL.X264.AAC-BTxiaba\\EP61.Ruyis.Royal.Love.in.the.Palace.2018.1080p.WEB-DL.X264.AAC-BTxiaba.mp4'
    #file_id = 'D:\\Downloads\\glibc-2.14.tar.gz'
    #Upload(file_path)
    ol = OpenLoad(g_login_id, g_login_key)
    result_info = 0
    try:
        result_info = ol.upload_file(file_path)
    except Exception as e:
        print(e)
    print(result_info)


if __name__ == "__main__":
    main()

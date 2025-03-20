from magika import Magika

def get_ext_and_mime(file_content: bytes) -> tuple[str, str]:
    magika = Magika()
    res = magika.identify_bytes(file_content)
    return res.output.mime_type
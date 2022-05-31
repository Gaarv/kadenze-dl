import kadenze_dl.utils as utils


def test_extract_filename():
    video_url = (
        "https://cdnc-prod-assets-private.kadenze.com/uploads/lecture_medium/4894/file/Reb_L5_720.mp4?Expires"
        "=1482662443\u0026Signature=QklHU9hV7z2gwVp9yYfN21IITWxPZnPa7c3QOUByerXthMHnGy7-PfWvw~jrk5bE6sNtj2uee"
        "gCiGNsusW3ummw0zQoNzO4e592eduSgP6SuN0axaqsdqiYGHHDG0dExRD~DepPmG1vSat2lJ3d8SOA0mYOfYMYz5Qk-oJd-wRHsx"
        "LQPKLhTW5sOD6OjSSajr7Qruu0s5Ej-5WKm4XLdLORz6q~OJEnye~ra~HsXhxqOfEDxoUYojvQZZNVdSRXUSZigEJ7vgYyNop-N7"
        "~HVRUGjXU~Z~NsB3LtFctaEvoNWd3CMVH~zwHmTKEF1rmDDb2To~ABS6t8sXREUdZ36pQ__\u0026Key-Pair-Id=APKAIPB43QU"
        "CA2NXZVSQmp4"
    )
    filename = utils.extract_filename(video_url)
    assert filename == "Reb_L5_720.mp4"


CONFIG_FILE_NAME = ".portly.ini"

CONFIG_FILE_TEMPLATE = """;
; Config file for Mr Portly.
;
[paths]
downloads = .\portal-content

;
; Add a new portal environment by giving it a name in [square brackets]
; and setting the url, user, and passwd properties.  Each section 
; will need to be unique.
;
[agol]
url = https://qgsp.maps.arcgis.com
user = wheresjacky
passwd = qwerty12

[myportal]
url = https://billabong.maps.arcgis.com
user = banjop
passwd = jollyjumbuck
"""

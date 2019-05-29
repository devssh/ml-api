curl -XPOST 'twmlapi.com/face/get_bounding_rects' -F "pimage=@/Users/devashishsood/Downloads/faces.png" -F "auth=c9095970345d"

curl -XPOST 'twmlapi.com/gender/extract_from_image' -F "pimage=@/Users/devashishsood/Documents/devashish.png" -F "auth=c9095970345d"

curl -XPOST 'twmlapi.com/gender/extract_from_name' -d '{"names": "devashish,gayathri", "auth": "c9095970345d"}'


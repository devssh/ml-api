curl -XPOST 'localhost:5001/face/get_bounding_rects' -F "pimage=@/Users/devashishsood/Downloads/faces.png" -F "auth=c9095970345d"

curl -XPOST 'localhost:5001/gender/extract_from_image' -F "pimage=@/Users/devashishsood/Documents/devashish.png" -F "auth=c9095970345d"

curl -XPOST 'localhost:5001/gender/extract_from_name' -d '{"names": "devashish,gayathri", "auth": "c9095970345d"}'

curl -XPOST 'localhost:5001/aws/translate' -d '{"Text": "Buongiorno","SourceLanguageCode": "it", "TargetLanguageCode":"en","auth":"Cc9095970345d"}'

curl -XPOST 'localhost:5001/aws/speech' -d '{"Text": "danke Devashish Sood, I am polly","auth":"Cc9095970345d"}' --output output.mp3
import fs from 'fs';
import express from 'express';
import multer from "multer";
import aws from 'aws-sdk';
import stream from 'stream';

const config = await JSON.parse(fs.readFileSync('./config.json', (err) => {
  console.log(`Error reading config file: ${err}`);
}));

const app = express();

app.listen(config.serverSettings.port).setTimeout(config.serverSettings.timeout);

const S3 = new aws.S3({
  endpoint: config.aws.endpoint,
  accessKeyId: config.aws.accessKeyID,
  secretAccessKey: config.aws.secretAccessKey,
  maxRetries: 10
});

//Create multer stream to send directly to AWS
const uploadStream = (key) => {
  let streamPass = new stream.PassThrough();
  const bucketParams = {
    Bucket: config.aws.bucket,
    Key: key,
    Body: streamPass,
    ACL: 'public-read'
  };
  let streamPromise = S3.upload(bucketParams, {
    partSize: 10 * 1024 * 1024,
    queueSize: 5
  }, (err, data) => {
    if (err) {
      console.log(`File upload failed: ${err}`);
    } else {
      console.log(`Upload stream: ${data}`);
    }
  }).promise();
  return {
    streamPass: streamPass,
    streamPromise: streamPromise
  }
}

class CustomStorage {
  _handleFile(req, file, cb) {
    let key = file.originalname;
    let { streamPass, streamPromise } = uploadStream(key);
    file.stream.pipe(streamPass)
    streamPromise.then(() => cb(null, {}))
  }
}

const storage = new CustomStorage();
const upload = multer({storage});

app.get('/', (req, res) => {
  res.writeHead(200, {'Content-Type':'text/html'});
    res.write(`Please upload your file below:

    
    <form action="/uploadFile" method="post" enctype="multipart/form-data">
    <input type="file" name="fileToUpload">
    
    <input type="submit">
    </form>`);
    return res.end();
});

app.post('/uploadFile', upload.single('fileToUpload'), async(req, res) => {
  console.log('Processing file...');
  try {
    res.write('File successfully uploaded.');
    console.log('File successfully uploaded.');
  } catch (err) {
    res.write(`File upload failed: ${err}`);
    console.log(`File upload failed: ${err}`);
  } finally {
    res.end();
  }
});
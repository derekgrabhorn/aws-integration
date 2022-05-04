import http from 'http';
import fs from 'fs';
import formidable from 'formidable';
import xml2js from "xml2js";
import fetch from "node-fetch";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const config = await JSON.parse(fs.readFileSync('./config.json', (err) => {
  console.log(`Error reading config file: ${err}`);
}));

const s3Client = new S3Client({
  credentials: {
      accessKeyId: config.aws.accessKeyID,
      secretAccessKey: config.aws.secretAccessKey
  },
  region: config.aws.region
});

http.createServer((req, res) => {
  if (req.url == '/fileupload') {
    console.log('Processing file...');
    var form = new formidable.IncomingForm();
    form.parse(req, async (err, fields, files) => {
      let rawData = fs.readFileSync(files.fileToUpload.filepath)
        try {
          await sendToAWS(rawData, files.fileToUpload.originalFilename);
          res.write('File successfully uploaded.');
          console.log('File successfully uploaded.');
        } catch(err) {
          res.write(`File failed to upload: ${err}`);
          console.log(`File failed to upload: ${err}`);
        }          
      res.end();
    });
  } else {
    res.writeHead(200, {'Content-Type':'text/html'});
    res.write(`Please upload your file below:

    
    <form action="fileupload" method="post" enctype="multipart/form-data">
    <input type="file" name="fileToUpload">
    
    <input type="submit">
    </form>`);
    return res.end();
  }
}).listen(config.serverSettings.port).setTimeout(config.serverSettings.timeout);

const sendToAWS = async (uploadedFile, filename) => {
  try {
    // Create a command to put the object in the S3 bucket
    const command = new PutObjectCommand({
      Bucket: config.aws.bucket,
      Key: `${filename}`,
    });

    // Create the presigned URL
    const signedUrl = await getSignedUrl(s3Client, command, {
      expiresIn: 43200,
    });

    //Upload the document with the presigned URL
    const response = await fetch(signedUrl, {method: 'PUT', body: uploadedFile});

    //Parse XML response from AWS to see if there was an error
    let xml = await response.text();
    let parser = new xml2js.Parser();
    let awsError;
    if(xml) {
      let hasError = parser.parseString(xml, (err, result) => {
        result.Error ? true : false;
        awsError = `CODE: ${result.Error.Code[0]}, MESSAGE: ${result.Error.Message[0]}`
      });

      if (hasError) {
        throw new Error(awsError);
        }
    }
  } catch (err) {
    console.log(`Error creating presigned URL ${err}`);
    throw Error(err);
  }
};

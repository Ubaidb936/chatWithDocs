import React, { useState } from "react";

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    // Logic to upload the file (e.g., using fetch or Axios)
    if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile);

      // Example: Upload using fetch
      fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("File uploaded successfully:", data);
        })
        .catch((error) => {
          console.error("Error uploading file:", error);
        });
    }
  };

  return (
    <div>
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
    </div>
    <div>
    <input type="text" onChange={() => console.log("sending text")} />
    <button>Submit</button>
  </div>
  </div>

  );
};

export default FileUpload;

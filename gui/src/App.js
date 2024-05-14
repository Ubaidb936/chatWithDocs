import React, { useEffect, useState } from "react";
import { FaFileUpload } from "react-icons/fa";
import "./App.css";

const App = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [textValue, setTextValue] = useState("");
  const [fileUploaded, setFileUploaded] = useState(false);
  const [uploading, setUploading] = useState(false); // State to track upload status
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetch("/reset", {
      method: "GET",
    });
  }, []);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    uploadFile(file);
  };

  const uploadFile = (file) => {
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      setUploading(true); // Set uploading to true when starting upload

      fetch("/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("File uploaded successfully:", data);
          setFileUploaded(true);
          setUploading(false); // Reset uploading state after upload is complete
        })
        .catch((error) => {
          console.error("Error uploading file:", error);
          setUploading(false); // Reset uploading state on error
        });
    }
  };

  const handleTextChange = (event) => {
    setTextValue(event.target.value);
  };

  const handleText = () => {
    if (textValue) {
      setMessages((prevMessages) => [...prevMessages, textValue]);
      // Send text message to server
      fetch(`/search?query=${textValue}`, {
        method: "GET",
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Search result:", data);
          setMessages((prevMessages) => [...prevMessages, data]);
        })
        .catch((error) => {
          console.error("Error:", error);
        });

      setTextValue(""); // Clear the text input after sending
    }
  };

  return (
    <div className="container">
      <div className="chatContainer">
        <div className="chatHeader">
          <h2>Chat</h2>
        </div>
        <ul className="chatMessages">
          {messages.map((message, index) => (
            <li key={index} className={index % 2 === 0 ? "even" : "odd"}>
              {message}
            </li>
          ))}
        </ul>
      </div>

      <div className="bottomBar">
        <div className="inputContainer">
          {!fileUploaded && (
            <label htmlFor="fileUpload" className="fileUploadButton">
              <input
                type="file"
                id="fileUpload"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
              {uploading ? (
                <div className="uploadIndicator">Uploading...</div>
              ) : (
                <FaFileUpload />
              )}
            </label>
          )}
          <input
            type="text"
            placeholder="Type a message..."
            value={textValue}
            onChange={handleTextChange}
          />
          <button onClick={handleText}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default App;

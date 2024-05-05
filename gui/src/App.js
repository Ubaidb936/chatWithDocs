import React, { useState } from "react";
import { FaFileUpload } from "react-icons/fa";
import "./App.css";

const App = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [textValue, setTextValue] = useState("");
  const [fileUploaded, setFileUploaded] = useState(false);
  const [messages, setMessages] = useState([]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    uploadFile(file);
  };

  const uploadFile = (file) => {
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("File uploaded successfully:", data);
          setFileUploaded(true);
        })
        .catch((error) => {
          console.error("Error uploading file:", error);
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
      fetch(`http://localhost:8000/search?query=${textValue}`, {
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

      // Add new message to state

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
              <FaFileUpload />
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

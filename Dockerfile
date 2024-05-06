# Use official Node.js image for building React app
FROM node:14 AS build-react

# Set working directory for React app
WORKDIR /app/gui

# Copy package.json and package-lock.json to install dependencies
COPY gui/package.json gui/package-lock.json ./

# Install Node.js dependencies
RUN npm install

# Copy all files from current directory to working directory
COPY gui/ .

# Build React app
RUN npm run build

# Use official Python image for running FastAPI app
FROM python:3.9-slim

# Set working directory for FastAPI app
WORKDIR /app

# Copy requirements.txt to install Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy built React app from previous stage
COPY --from=build-react /app/gui/build /app/gui/build

COPY main.py .
# Expose port for FastAPI app
EXPOSE 8000

# Command to run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


"use client";

import React, { useState } from "react";
import { Button } from "@/app/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/ui/card";
import { Progress } from "@/app/ui/progress";
import { UploadCloud, CheckCircle, AlertCircle, FileSpreadsheet } from "lucide-react";
import { useTranslation } from "react-i18next";
import { lusitana } from '@/app/ui/fonts';
import Breadcrumbs from '@/app/ui/breadcrumbs';

const FileUploadForm = () => {
  const { t } = useTranslation('common');
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);

  interface FileChangeEvent extends React.ChangeEvent<HTMLInputElement> {
    target: HTMLInputElement & EventTarget;
  }

  const handleFileChange = (event: FileChangeEvent) => {
    const selectedFile = event.target.files?.[0] || null;
    setFile(selectedFile);
    setMessage("");
    setUploadStatus('idle');
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage(t('uploadNoFile'));
      setUploadStatus('error');
      return;
    }

    // Validate file type
    if (!file.name.endsWith('.xlsx')) {
      setMessage(t('uploadInvalidFileType'));
      setUploadStatus('error');
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setMessage(t('uploadUploading'));
    setIsUploading(true);
    setUploadStatus('uploading');

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        const newProgress = prev + Math.random() * 10;
        return Math.min(newProgress, 95); // Cap at 95% until actually complete
      });
    }, 300);

    try {
      const response = await fetch("/api/seed", {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const result = await response.json();
      setMessage(result.message);

      if (response.ok) {
        setUploadStatus('success');
        setFile(null);
        
        // Reset file input by clearing the value
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setUploadStatus('error');
      }
    } catch (error) {
      console.error("Upload error:", error);
      setMessage(t('uploadError') || "An error occurred during upload");
      setUploadStatus('error');
      clearInterval(progressInterval);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <>
      <Breadcrumbs
        breadcrumbs={[
          { label: t('breadcrumbHome'), href: '/' },
          { label: t('breadcrumbUpload'), href: '/upload', active: true }
        ]}
      />
      
      <h1 className={`${lusitana.className} mb-6 text-2xl md:text-3xl font-bold text-mint-11 dark:text-mint-9`}>
        {t('uploadTitle')}
      </h1>
      
      <div className="w-full max-w-lg mx-auto">
        <Card className="border border-mint-6 dark:border-mint-8 bg-white dark:bg-zinc-900 shadow-sm">
          <CardHeader className="pb-0">
            <CardTitle className="text-mint-11 dark:text-mint-9 text-xl">
              {t('uploadSubtitle')}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="flex flex-col space-y-6">
              {/* Upload area */}
              <div 
                className={`
                  relative border-2 border-dashed rounded-lg p-6 
                  flex flex-col items-center justify-center space-y-4 text-center
                  transition-colors
                  ${!file && 'hover:bg-mint-1 dark:hover:bg-zinc-800'}
                  ${file ? 'bg-mint-2 dark:bg-zinc-800 border-mint-6 dark:border-mint-8' : 
                    'border-gray-300 dark:border-gray-700'}
                `}
              >
                <input
                  id="file-upload"
                  type="file"
                  accept=".xlsx"
                  onChange={handleFileChange}
                  disabled={isUploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                />
                
                <div className="flex flex-col items-center">
                  {file ? (
                    <div className="bg-mint-3 dark:bg-mint-8/30 p-3 rounded-full">
                      <FileSpreadsheet className="w-8 h-8 text-mint-11 dark:text-mint-9" />
                    </div>
                  ) : (
                    <div className="bg-mint-3 dark:bg-zinc-800 p-3 rounded-full">
                      <UploadCloud className="w-8 h-8 text-mint-11 dark:text-mint-9" />
                    </div>
                  )}
                  
                  {file ? (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-mint-11 dark:text-mint-9">
                        {file.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  ) : (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-mint-11 dark:text-mint-9">
                        {t('uploadDragDrop')}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {t('uploadSupportedFormats')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Progress bar */}
              {isUploading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-mint-11 dark:text-mint-9">Uploading...</span>
                    <span className="text-mint-11 dark:text-mint-9">{Math.round(uploadProgress)}%</span>
                  </div>
                  <Progress 
                    value={uploadProgress} 
                    className="h-2 bg-mint-3 dark:bg-zinc-800"
                  />
                </div>
              )}
              
              {/* Status message */}
              {message && !isUploading && (
                <div className={`
                  flex items-center p-3 rounded-md text-sm
                  ${uploadStatus === 'success' ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : ''}
                  ${uploadStatus === 'error' ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400' : ''}
                `}>
                  {uploadStatus === 'success' && <CheckCircle className="w-5 h-5 mr-2 flex-shrink-0" />}
                  {uploadStatus === 'error' && <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />}
                  {message}
                </div>
              )}
              
              {/* Upload button */}
              <Button
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="w-full bg-mint-9 hover:bg-mint-10 text-white dark:bg-mint-8 dark:hover:bg-mint-9 dark:text-black h-10 transition-colors"
              >
                <UploadCloud className="w-5 h-5 mr-2" />
                <span>
                  {isUploading 
                    ? (t('uploadUploading')) 
                    : (t('uploadButton'))}
                </span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
};

export default FileUploadForm;
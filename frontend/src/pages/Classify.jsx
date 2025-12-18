import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import { Upload, Camera, Loader2, Trash2, Recycle, AlertTriangle, Leaf, Info, ImageIcon } from 'lucide-react'
import { classifyImage } from '../services/api'
import { saveDetection } from '../utils/storage'
import ResultCard from '../components/ResultCard'

const Classify = () => {
  const [mode, setMode] = useState('upload') // 'upload' or 'camera'
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)
  const webcamRef = useRef(null)

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedImage(file)
      setImagePreview(URL.createObjectURL(file))
      setResult(null)
      setError(null)
    }
  }

  const capturePhoto = () => {
    const imageSrc = webcamRef.current.getScreenshot()
    if (imageSrc) {
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
          setSelectedImage(file)
          setImagePreview(imageSrc)
          setResult(null)
          setError(null)
        })
    }
  }

  const handleClassify = async () => {
    if (!selectedImage) return

    setIsLoading(true)
    setError(null)
    
    try {
      const data = await classifyImage(selectedImage)
      setResult(data)
      
      // Save to history
      saveDetection({
        ...data,
        imageUrl: imagePreview,
        source: mode
      })
    } catch (err) {
      setError(err.message || 'Failed to classify image')
    } finally {
      setIsLoading(false)
    }
  }

  const resetApp = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setResult(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getIconForClass = (className) => {
    const icons = {
      'Recyclable': Recycle,
      'Non-Recyclable': Trash2,
      'Hazardous': AlertTriangle,
      'Organic': Leaf
    }
    return icons[className] || Info
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Classify Waste</h1>
        <p className="text-gray-600">Upload an image or use your camera to classify waste</p>
      </div>

      {/* Mode Selector */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={() => {
            setMode('upload')
            resetApp()
          }}
          className={`flex-1 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
            mode === 'upload'
              ? 'bg-primary-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-500'
          }`}
        >
          <ImageIcon className="w-5 h-5" />
          Upload Image
        </button>
        <button
          onClick={() => {
            setMode('camera')
            resetApp()
          }}
          className={`flex-1 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
            mode === 'camera'
              ? 'bg-primary-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-500'
          }`}
        >
          <Camera className="w-5 h-5" />
          Use Camera
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Panel - Upload/Camera */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              {mode === 'upload' ? 'Upload Image' : 'Camera'}
            </h2>

            {mode === 'upload' ? (
              // Upload Mode
              <>
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-primary-500 hover:bg-primary-50/50 transition-all"
                >
                  {imagePreview ? (
                    <div className="relative">
                      <div className={`relative p-1 rounded-lg ${
                        result ? 'border-8 shadow-xl' : ''
                      }`} style={{
                        borderColor: result ? result.prediction.color : 'transparent'
                      }}>
                        <img
                          src={imagePreview}
                          alt="Selected"
                          className="max-w-full max-h-96 mx-auto rounded-lg shadow-md"
                        />
                        {result && (
                          <div className="absolute top-3 left-3 px-3 py-2 rounded-lg font-bold text-white shadow-lg" 
                            style={{ backgroundColor: result.prediction.color }}>
                            {result.prediction.class}
                          </div>
                        )}
                      </div>
                      <div className="absolute top-2 right-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            resetApp()
                          }}
                          className="bg-white/90 backdrop-blur-sm p-2 rounded-lg shadow-lg hover:bg-red-50 transition-colors"
                        >
                          <Trash2 className="w-5 h-5 text-red-600" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="py-12">
                      <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Upload className="w-10 h-10 text-primary-600" />
                      </div>
                      <p className="text-gray-700 font-medium mb-2">Click to upload image</p>
                      <p className="text-sm text-gray-500">
                        Supports: JPG, PNG, WEBP (Max 10MB)
                      </p>
                    </div>
                  )}
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </>
            ) : (
              // Camera Mode
              <div className="relative">
                {imagePreview ? (
                  <div className="relative">
                    <div className={`relative p-1 rounded-lg ${
                      result ? 'border-8 shadow-xl' : ''
                    }`} style={{
                      borderColor: result ? result.prediction.color : 'transparent'
                    }}>
                      <img
                        src={imagePreview}
                        alt="Captured"
                        className="w-full rounded-lg shadow-md"
                      />
                      {result && (
                        <div className="absolute top-3 left-3 px-3 py-2 rounded-lg font-bold text-white shadow-lg" 
                          style={{ backgroundColor: result.prediction.color }}>
                          {result.prediction.class}
                        </div>
                      )}
                    </div>
                    <div className="absolute top-2 right-2">
                      <button
                        onClick={resetApp}
                        className="bg-white/90 backdrop-blur-sm p-2 rounded-lg shadow-lg hover:bg-red-50 transition-colors"
                      >
                        <Trash2 className="w-5 h-5 text-red-600" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="relative">
                    <Webcam
                      ref={webcamRef}
                      screenshotFormat="image/jpeg"
                      className="w-full rounded-lg shadow-md"
                      videoConstraints={{
                        width: 1280,
                        height: 720,
                        facingMode: "environment"
                      }}
                    />
                    <div className="absolute inset-0 border-2 border-primary-500/50 rounded-lg pointer-events-none" />
                  </div>
                )}

                {!imagePreview && (
                  <button
                    onClick={capturePhoto}
                    className="w-full mt-4 bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 shadow-lg shadow-primary-600/30"
                  >
                    <Camera className="w-5 h-5" />
                    Capture Photo
                  </button>
                )}
              </div>
            )}

            {/* Action Buttons */}
            {selectedImage && (
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleClassify}
                  disabled={isLoading}
                  className="flex-1 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 shadow-lg shadow-primary-600/30"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Classifying...
                    </>
                  ) : (
                    <>
                      <Recycle className="w-5 h-5" />
                      Classify Waste
                    </>
                  )}
                </button>
                
                <button
                  onClick={resetApp}
                  disabled={isLoading}
                  className="px-6 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 text-gray-700 py-3 rounded-lg font-medium transition-colors"
                >
                  {mode === 'camera' ? 'Retake' : 'Reset'}
                </button>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Tips */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <Info className="w-5 h-5" />
              Tips for Best Results
            </h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>• Ensure good lighting in the image</li>
              <li>• Keep the waste item centered</li>
              <li>• Avoid blurry or dark photos</li>
              <li>• One item at a time works best</li>
              {mode === 'camera' && <li>• Hold camera steady when capturing</li>}
            </ul>
          </div>
        </div>

        {/* Right Panel - Results */}
        <div>
          {result ? (
            <ResultCard result={result} getIcon={getIconForClass} />
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
              <div className="opacity-50">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Recycle className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-400 mb-2">
                  No Classification Yet
                </h3>
                <p className="text-gray-500">
                  {mode === 'upload' ? 'Upload an image' : 'Capture a photo'} to see the classification results
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Classify
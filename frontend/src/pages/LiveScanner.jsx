import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import { Camera, Loader2, Trash2, Recycle, AlertTriangle, Leaf, Info } from 'lucide-react'
import { classifyImage } from '../services/api'
import { saveDetection } from '../utils/storage'
import ResultCard from '../components/ResultCard'

const LiveScanner = () => {
  const [imagePreview, setImagePreview] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const webcamRef = useRef(null)

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
        source: 'camera'
      })
    } catch (err) {
      setError(err.message || 'Failed to classify image')
    } finally {
      setIsLoading(false)
    }
  }

  const resetCamera = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setResult(null)
    setError(null)
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
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Live Scanner</h1>
        <p className="text-gray-600">Use your camera for real-time waste detection</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Panel - Camera */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Camera Feed</h2>

            <div className="relative">
              {imagePreview ? (
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Captured"
                    className="w-full rounded-lg shadow-md"
                  />
                  <div className="absolute top-2 right-2">
                    <button
                      onClick={resetCamera}
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
            </div>

            {/* Action Buttons */}
            <div className="mt-6">
              {!imagePreview ? (
                <button
                  onClick={capturePhoto}
                  className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 shadow-lg shadow-primary-600/30"
                >
                  <Camera className="w-5 h-5" />
                  Capture Photo
                </button>
              ) : (
                <div className="flex gap-3">
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
                    onClick={resetCamera}
                    disabled={isLoading}
                    className="px-6 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 text-gray-700 py-3 rounded-lg font-medium transition-colors"
                  >
                    Retake
                  </button>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Camera Tips */}
          <div className="bg-green-50 border border-green-200 rounded-xl p-6">
            <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
              <Info className="w-5 h-5" />
              Camera Tips
            </h3>
            <ul className="space-y-2 text-sm text-green-800">
              <li>• Hold the camera steady</li>
              <li>• Ensure adequate lighting</li>
              <li>• Position item in center of frame</li>
              <li>• Keep camera at arm's length</li>
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
                  <Camera className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-400 mb-2">
                  No Scan Yet
                </h3>
                <p className="text-gray-500">
                  Capture a photo to see the classification results
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default LiveScanner
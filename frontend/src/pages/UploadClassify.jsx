import { useState, useRef } from 'react'
import { Upload, Loader2, Trash2, Recycle, AlertTriangle, Leaf, Info } from 'lucide-react'
import { classifyImage } from '../services/api'
import { saveDetection } from '../utils/storage'
import ResultCard from '../components/ResultCard'

const UploadClassify = () => {
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedImage(file)
      setImagePreview(URL.createObjectURL(file))
      setResult(null)
      setError(null)
    }
  }

  const handleClassify = async () => {
    if (!selectedImage) return

    setIsLoading(true)
    setError(null)
    
    try {
      const data = await classifyImage(selectedImage)
      setResult(data)
      
      // Save to history with image preview
      saveDetection({
        ...data,
        imageUrl: imagePreview,
        source: 'upload'
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
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Upload & Classify</h1>
        <p className="text-gray-600">Upload an image of waste to identify its category</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Panel - Upload */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Image</h2>

            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-primary-500 hover:bg-primary-50/50 transition-all"
            >
              {imagePreview ? (
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Selected"
                    className="max-w-full max-h-96 mx-auto rounded-lg shadow-md"
                  />
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
                  Reset
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
                  Upload an image to see the classification results
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default UploadClassify
import { useState, useEffect } from 'react'
import { Trash2, Recycle, AlertTriangle, Leaf, Calendar, Clock, Trash, Download } from 'lucide-react'
import { getDetections, deleteDetection, clearAllDetections } from '../utils/storage'

const PastDetections = () => {
  const [detections, setDetections] = useState([])
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadDetections()
  }, [])

  const loadDetections = () => {
    setDetections(getDetections())
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this detection?')) {
      deleteDetection(id)
      loadDetections()
    }
  }

  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to delete all detections? This cannot be undone.')) {
      clearAllDetections()
      loadDetections()
    }
  }

  const getIconForClass = (className) => {
    const icons = {
      'Recyclable': Recycle,
      'Non-Recyclable': Trash2,
      'Hazardous': AlertTriangle,
      'Organic': Leaf
    }
    return icons[className] || Recycle
  }

  const getColorForClass = (className) => {
    const colors = {
      'Recyclable': { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
      'Non-Recyclable': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
      'Hazardous': { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
      'Organic': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' }
    }
    return colors[className] || colors['Recyclable']
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  const filteredDetections = filter === 'all' 
    ? detections 
    : detections.filter(d => d.prediction?.class === filter)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Past Detections</h1>
            <p className="text-gray-600">View and manage your classification history</p>
          </div>
          
          {detections.length > 0 && (
            <button
              onClick={handleClearAll}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <Trash className="w-4 h-4" />
              Clear All
            </button>
          )}
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {['all', 'Recyclable', 'Non-Recyclable', 'Hazardous', 'Organic'].map((category) => (
            <button
              key={category}
              onClick={() => setFilter(category)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${
                filter === category
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-500'
              }`}
            >
              {category === 'all' ? 'All' : category}
            </button>
          ))}
        </div>
      </div>

      {/* Detections Grid */}
      {filteredDetections.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-16 text-center">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Calendar className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Detections Found</h3>
          <p className="text-gray-500">
            {filter === 'all' 
              ? 'Start classifying waste items to see them here'
              : `No ${filter} items detected yet`
            }
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDetections.map((detection) => {
            const Icon = getIconForClass(detection.prediction?.class)
            const colors = getColorForClass(detection.prediction?.class)
            
            return (
              <div
                key={detection.id}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-xl transition-all group"
              >
                {/* Image */}
                {detection.imageUrl && (
                  <div className="aspect-video bg-gray-100 overflow-hidden">
                    <img
                      src={detection.imageUrl}
                      alt="Detection"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                  </div>
                )}

                {/* Content */}
                <div className="p-4">
                  {/* Classification Badge */}
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 ${colors.bg} ${colors.border} border rounded-full mb-3`}>
                    <Icon className={`w-4 h-4 ${colors.text}`} />
                    <span className={`text-sm font-medium ${colors.text}`}>
                      {detection.prediction?.class}
                    </span>
                  </div>

                  {/* Confidence */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Confidence</span>
                      <span className="font-semibold text-gray-800">
                        {(detection.prediction?.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all"
                        style={{ width: `${detection.prediction?.confidence * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Timestamp */}
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(detection.timestamp)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTime(detection.timestamp)}
                    </div>
                  </div>

                  {/* Source Badge */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                      {detection.source === 'camera' ? 'Live Scan' : 'Upload'}
                    </span>
                    
                    <button
                      onClick={() => handleDelete(detection.id)}
                      className="p-2 hover:bg-red-50 rounded-lg transition-colors group"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 group-hover:text-red-600 transition-colors" />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Stats Footer */}
      {detections.length > 0 && (
        <div className="mt-8 bg-gradient-to-r from-primary-500 to-emerald-600 rounded-xl p-6 text-white">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-3xl font-bold">{detections.length}</p>
              <p className="text-sm text-green-100">Total Scans</p>
            </div>
            <div>
              <p className="text-3xl font-bold">
                {detections.filter(d => d.prediction?.class === 'Recyclable').length}
              </p>
              <p className="text-sm text-green-100">Recyclable</p>
            </div>
            <div>
              <p className="text-3xl font-bold">
                {detections.filter(d => d.prediction?.class === 'Hazardous').length}
              </p>
              <p className="text-sm text-green-100">Hazardous</p>
            </div>
            <div>
              <p className="text-3xl font-bold">
                {detections.filter(d => d.prediction?.class === 'Organic').length}
              </p>
              <p className="text-sm text-green-100">Organic</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PastDetections
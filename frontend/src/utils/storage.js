/**
 * Utility functions for storing and retrieving past detections
 */

const STORAGE_KEY = 'ecovision_detections'

/**
 * Save a detection to local storage
 */
export const saveDetection = (detection) => {
  try {
    const detections = getDetections()
    
    const newDetection = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...detection
    }
    
    detections.unshift(newDetection) // Add to beginning
    
    // Keep only last 100 detections
    const limitedDetections = detections.slice(0, 100)
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(limitedDetections))
    
    return newDetection
  } catch (error) {
    console.error('Error saving detection:', error)
    return null
  }
}

/**
 * Get all detections from local storage
 */
export const getDetections = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : []
  } catch (error) {
    console.error('Error getting detections:', error)
    return []
  }
}

/**
 * Delete a detection by ID
 */
export const deleteDetection = (id) => {
  try {
    const detections = getDetections()
    const filtered = detections.filter(d => d.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
    return true
  } catch (error) {
    console.error('Error deleting detection:', error)
    return false
  }
}

/**
 * Clear all detections
 */
export const clearAllDetections = () => {
  try {
    localStorage.removeItem(STORAGE_KEY)
    return true
  } catch (error) {
    console.error('Error clearing detections:', error)
    return false
  }
}

/**
 * Get detection statistics
 */
export const getDetectionStats = () => {
  const detections = getDetections()
  
  const stats = {
    total: detections.length,
    recyclable: 0,
    nonRecyclable: 0,
    hazardous: 0,
    organic: 0
  }
  
  detections.forEach(d => {
    const className = d.prediction?.class || ''
    if (className.includes('Recyclable') && !className.includes('Non')) {
      stats.recyclable++
    } else if (className.includes('Non-Recyclable')) {
      stats.nonRecyclable++
    } else if (className.includes('Hazardous')) {
      stats.hazardous++
    } else if (className.includes('Organic')) {
      stats.organic++
    }
  })
  
  return stats
}
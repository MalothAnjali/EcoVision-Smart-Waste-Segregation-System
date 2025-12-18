/**
 * API service for communicating with the backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

/**
 * Classify a waste image
 * @param {File} imageFile - The image file to classify
 * @returns {Promise<Object>} Classification results
 */
export const classifyImage = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('file', imageFile)

    const response = await api.post('/classify', formData)
    return response.data
  } catch (error) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || 'Classification failed')
    } else if (error.request) {
      // No response received
      throw new Error('Unable to connect to server. Make sure the backend is running.')
    } else {
      // Other errors
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
}

/**
 * Get available waste classes
 * @returns {Promise<Object>} List of classes
 */
export const getClasses = async () => {
  try {
    const response = await api.get('/classes')
    return response.data
  } catch (error) {
    console.error('Error fetching classes:', error)
    // Return default classes if API fails
    return {
      classes: [
        { id: 0, name: 'Recyclable', color: '#22c55e', description: 'Materials that can be recycled' },
        { id: 1, name: 'Non-Recyclable', color: '#ef4444', description: 'Items that cannot be recycled' },
        { id: 2, name: 'Hazardous', color: '#eab308', description: 'Dangerous waste requiring special handling' },
        { id: 3, name: 'Organic', color: '#3b82f6', description: 'Biodegradable waste' }
      ]
    }
  }
}

/**
 * Get model information
 * @returns {Promise<Object>} Model details
 */
export const getModelInfo = async () => {
  try {
    const response = await api.get('/model/info')
    return response.data
  } catch (error) {
    console.error('Error fetching model info:', error)
    return { loaded: false, message: 'Unable to fetch model information' }
  }
}

/**
 * Send a message to the chatbot
 * @param {string} message - User's message
 * @param {Array} history - Conversation history
 * @returns {Promise<Object>} Chatbot response
 */
export const sendChatMessage = async (message, history = []) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chatbot/chat`, {
      message,
      history
    }, {
      headers: {
        'Content-Type': 'application/json',
      }
    })
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get chatbot response')
    } else if (error.request) {
      throw new Error('Unable to connect to chatbot. Make sure the backend is running and Gemini API key is configured.')
    } else {
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
}

/**
 * Get a quick environmental tip
 * @returns {Promise<Object>} Random tip
 */
export const getQuickTip = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/chatbot/quick-tip`)
    return response.data
  } catch (error) {
    console.error('Error fetching quick tip:', error)
    return { tip: '♻️ Remember: Reduce, Reuse, Recycle!', success: false }
  }
}

export default api
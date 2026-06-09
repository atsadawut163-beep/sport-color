// Configuration for the Sport Color web application
// Automatically detects if running locally or in production
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:')
    ? 'http://127.0.0.1:8000'
    : 'https://sport-color-backend.onrender.com'; // Replace this with your actual Render/Railway backend URL once deployed

import React, { useState, useEffect } from 'react';
import './App.css';

// API URL configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://calcdynamics-api-env.eba-zku5kvfn.us-east-1.elasticbeanstalk.com';
console.log('Using API URL:', API_URL);

function App() {
  const [activeTab, setActiveTab] = useState('equations');
  const [dimension, setDimension] = useState('1D');
  const [equationType, setEquationType] = useState('heat');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [parameters, setParameters] = useState({
    // Default parameters for 1D heat equation
    length: 1.0,
    time: 0.5,
    num_x: 50,
    num_t: 1000,
    diffusivity: 0.01,
    boundary_type: 'fixed',
    left_value: 0,
    right_value: 1,
    
    // Default parameters for 1D wave equation
    wave_speed: 1.0,
    
    // Default parameters for 1D Burgers equation
    viscosity: 0.01,
    initial_velocity: 0,
    
    // Default parameters for 2D heat equation
    width: 10.0,
    height: 10.0,
    mesh_density: 0.5,
    mesh_quality: 30,
    with_holes: false,
    hole_rows: 1,
    hole_cols: 1,
    hole_radius: 0.5,
    bottom_value: 0,
    top_value: 100,
  });
  const [availableTimes, setAvailableTimes] = useState([]);
  const [selectedTimes, setSelectedTimes] = useState([]);
  const [showIndividualPlots, setShowIndividualPlots] = useState(true);
  const [plots, setPlots] = useState({});

  // Update parameters when equation type changes
  useEffect(() => {
    if (equationType === 'heat') {
      setParameters(prev => ({
        ...prev,
        time: 0.5,
        num_x: 50,
        num_t: 1000,
        diffusivity: 0.01,
        boundary_type: 'fixed',
        left_value: 0,
        right_value: 1,
      }));
    } else if (equationType === 'wave') {
      setParameters(prev => ({
        ...prev,
        time: 1.0,
        num_x: 100,
        num_t: 500,
        wave_speed: 1.0,
      }));
    } else if (equationType === 'burgers') {
      setParameters(prev => ({
        ...prev,
        time: 1.0,
        num_x: 100,
        viscosity: 0.01,
        initial_velocity: 0,
      }));
    }
  }, [equationType]);

  // Handle parameter changes
  const handleParameterChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // Handle checkboxes
    if (type === 'checkbox') {
      setParameters(prev => ({
        ...prev,
        [name]: checked
      }));
      return;
    }
    
    // Handle numeric inputs
    if (type === 'number' || type === 'range') {
      setParameters(prev => ({
        ...prev,
        [name]: parseFloat(value)
      }));
      return;
    }
    
    // Handle all other inputs
    setParameters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      let apiUrl = '';
      let requestData = {};
      
      // Determine API endpoint and prepare request data based on dimension and equation type
      if (dimension === '1D') {
        if (equationType === 'heat') {
          apiUrl = '/api/heat-equation';
          
          // Create initial temperature profile (sine wave)
          const initialTemp = Array.from({ length: parameters.num_x }, (_, i) => {
            const x = i / (parameters.num_x - 1) * parameters.length;
            return Math.sin(Math.PI * x / parameters.length);
          });
          
          requestData = {
            length: parameters.length,
            time: parameters.time,
            num_x: parameters.num_x,
            num_t: parameters.num_t,
            diffusivity: parameters.diffusivity,
            initial_temp: initialTemp,
            boundary_type: parameters.boundary_type,
            left_value: parameters.left_value,
            right_value: parameters.right_value
          };
        } else if (equationType === 'wave') {
          apiUrl = '/api/wave-equation';
          
          // Create initial displacement profile (sine wave)
          const initialDisplacement = Array.from({ length: parameters.num_x }, (_, i) => {
            const x = i / (parameters.num_x - 1) * parameters.length;
            return Math.sin(Math.PI * x / parameters.length);
          });
          
          // Initial velocity is zero everywhere
          const initialVelocity = Array(parameters.num_x).fill(parameters.initial_velocity);
          
          requestData = {
            length: parameters.length,
            time: parameters.time,
            num_x: parameters.num_x,
            num_t: parameters.num_t,
            wave_speed: parameters.wave_speed,
            initial_displacement: initialDisplacement,
            initial_velocity: initialVelocity,
            boundary_type: parameters.boundary_type,
            left_value: parameters.left_value,
            right_value: parameters.right_value
          };
        } else if (equationType === 'burgers') {
          apiUrl = '/api/burgers-equation';
          
          requestData = {
            dt: 0.001,
            T: parameters.time,
            nu: parameters.viscosity,
            n_newton_iter: 5,
            num_points: parameters.num_x,
            x_min: 0,
            x_max: parameters.length,
            left_value: parameters.left_value,
            right_value: parameters.right_value,
            ic_type: 'sine'  // or 'step'
          };
        }
      } else if (dimension === '2D') {
        apiUrl = '/api/heat-equation-2d';
        
        requestData = {
          width: parameters.width,
          height: parameters.height,
          mesh_density: parameters.mesh_density,
          mesh_quality: parameters.mesh_quality,
          with_holes: parameters.with_holes,
          hole_rows: parameters.hole_rows,
          hole_cols: parameters.hole_cols,
          hole_radius: parameters.hole_radius,
          bottom_value: parameters.bottom_value,
          top_value: parameters.top_value,
          left_value: parameters.left_value,
          right_value: parameters.right_value
        };
      }
      
      console.log(`Sending request to ${API_URL}${apiUrl} with data:`, requestData);
      
      // Create an AbortController to handle timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      try {
        const response = await fetch(`${API_URL}${apiUrl}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData),
          signal: controller.signal
        });
        
        clearTimeout(timeoutId); // Clear the timeout if the request completes
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to solve equation');
        }
        
        const data = await response.json();
        console.log('Received response:', data);
        
        setResults(data);
        
        // Set available times for time slider
        if (dimension === '1D' && data.t) {
          setAvailableTimes(data.t);
          setSelectedTime(data.t[Math.floor(data.t.length / 2)]); // Default to middle time
        }
        
        // For 1D equations, set selected times for individual plots
        if (dimension === '1D' && data.t) {
          const numTimes = data.t.length;
          const selectedIndices = [
            0,
            Math.floor(numTimes / 4),
            Math.floor(numTimes / 2),
            Math.floor(3 * numTimes / 4),
            numTimes - 1
          ];
          setSelectedTimes(selectedIndices.map(i => data.t[i]));
        }
        
        // For 2D heat equation, store the plots
        if (dimension === '2D' && data.plots) {
          setPlots(data.plots);
        }
        
      } catch (err) {
        console.error('Error:', err);
        if (err.name === 'AbortError') {
          setError('Request timed out. The calculation might be too complex or the server might be overloaded.');
        } else {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    }
  };

  // Handle dimension change
  const handleDimensionChange = (e) => {
    const newDimension = e.target.value;
    setDimension(newDimension);
    
    // Reset equation type based on dimension
    if (newDimension === '1D') {
      setEquationType('heat');
      
      // Set default parameters for 1D
      setParameters(prev => ({
        ...prev,
        length: 1.0,
        time: 0.5,
        num_x: 50,
        num_t: 1000,
        diffusivity: 0.01,
        boundary_type: 'fixed',
        left_value: 0,
        right_value: 1,
      }));
    } else if (newDimension === '2D') {
      setEquationType('heat');
      
      // Set default parameters for 2D
      setParameters(prev => ({
        ...prev,
        width: 10.0,
        height: 10.0,
        mesh_density: 0.5,
        mesh_quality: 30,
        with_holes: false,
        hole_rows: 1,
        hole_cols: 1,
        hole_radius: 0.5,
        bottom_value: 0,
        top_value: 100,
        left_value: 0,
        right_value: 0
      }));
    }
  };

  // Handle equation type change
  const handleEquationTypeChange = (e) => {
    const newEquationType = e.target.value;
    setEquationType(newEquationType);
  };

  // Function to regenerate plots with new time selections
  const regeneratePlots = async () => {
    if (!results || !results.x || !results.u || !results.t) {
      return;
    }
    
    try {
      // Find indices of selected times
      const timeIndices = selectedTimes.map(time => {
        return results.t.findIndex(t => Math.abs(t - time) < 1e-6);
      }).filter(index => index !== -1);
      
      // Generate individual plots
      const plotsData = {};
      
      // For 1D equations
      if (dimension === '1D') {
        for (let i = 0; i < timeIndices.length; i++) {
          const timeIndex = timeIndices[i];
          const time = results.t[timeIndex];
          const u_at_time = results.u[timeIndex];
          
          // Create plot data
          plotsData[`t_${i}`] = {
            x: results.x,
            y: u_at_time,
            time: time
          };
        }
      }
      
      setPlots(plotsData);
    } catch (err) {
      console.error('Error regenerating plots:', err);
      setError('Failed to regenerate plots: ' + err.message);
    }
  };

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // Reset state when changing tabs
    if (tab === 'equations') {
      setDimension('1D');
      setEquationType('heat');
    }
  };

  // Function to render equation parameters based on dimension and equation type
  const renderEquationParameters = () => {
    if (dimension === '1D') {
      return (
        <div className="equation-parameters">
          <div className="parameter-group">
            <label htmlFor="length">Domain Length:</label>
            <input
              type="number"
              id="length"
              name="length"
              min="0.1"
              step="0.1"
              value={parameters.length}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="time">Simulation Time:</label>
            <input
              type="number"
              id="time"
              name="time"
              min="0.01"
              step="0.01"
              value={parameters.time}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="num_x">Spatial Points:</label>
            <input
              type="number"
              id="num_x"
              name="num_x"
              min="10"
              max="500"
              step="10"
              value={parameters.num_x}
              onChange={handleParameterChange}
            />
          </div>
          
          {equationType !== 'burgers' && (
            <div className="parameter-group">
              <label htmlFor="num_t">Time Steps:</label>
              <input
                type="number"
                id="num_t"
                name="num_t"
                min="10"
                max="10000"
                step="10"
                value={parameters.num_t}
                onChange={handleParameterChange}
              />
            </div>
          )}
          
          {equationType === 'heat' && (
            <div className="parameter-group">
              <label htmlFor="diffusivity">Diffusivity:</label>
              <input
                type="number"
                id="diffusivity"
                name="diffusivity"
                min="0.001"
                max="1"
                step="0.001"
                value={parameters.diffusivity}
                onChange={handleParameterChange}
              />
            </div>
          )}
          
          {equationType === 'wave' && (
            <div className="parameter-group">
              <label htmlFor="wave_speed">Wave Speed:</label>
              <input
                type="number"
                id="wave_speed"
                name="wave_speed"
                min="0.1"
                max="10"
                step="0.1"
                value={parameters.wave_speed}
                onChange={handleParameterChange}
              />
            </div>
          )}
          
          {equationType === 'wave' && (
            <div className="parameter-group">
              <label htmlFor="initial_velocity">Initial Velocity:</label>
              <input
                type="number"
                id="initial_velocity"
                name="initial_velocity"
                step="0.1"
                value={parameters.initial_velocity}
                onChange={handleParameterChange}
              />
            </div>
          )}
          
          {equationType === 'burgers' && (
            <div className="parameter-group">
              <label htmlFor="viscosity">Viscosity:</label>
              <input
                type="number"
                id="viscosity"
                name="viscosity"
                min="0.001"
                max="1"
                step="0.001"
                value={parameters.viscosity}
                onChange={handleParameterChange}
              />
            </div>
          )}
          
          <div className="parameter-group">
            <label htmlFor="boundary_type">Boundary Conditions:</label>
            <select
              id="boundary_type"
              name="boundary_type"
              value={parameters.boundary_type}
              onChange={handleParameterChange}
            >
              <option value="fixed">Fixed (Dirichlet)</option>
              <option value="neumann">Neumann</option>
              <option value="periodic">Periodic</option>
            </select>
          </div>
          
          {parameters.boundary_type !== 'periodic' && (
            <>
              <div className="parameter-group">
                <label htmlFor="left_value">Left Boundary Value:</label>
                <input
                  type="number"
                  id="left_value"
                  name="left_value"
                  step="0.1"
                  value={parameters.left_value}
                  onChange={handleParameterChange}
                />
              </div>
              
              <div className="parameter-group">
                <label htmlFor="right_value">Right Boundary Value:</label>
                <input
                  type="number"
                  id="right_value"
                  name="right_value"
                  step="0.1"
                  value={parameters.right_value}
                  onChange={handleParameterChange}
                />
              </div>
            </>
          )}
        </div>
      );
    } else if (dimension === '2D') {
      return (
        <div className="equation-parameters">
          <div className="parameter-group">
            <label htmlFor="width">Domain Width:</label>
            <input
              type="number"
              id="width"
              name="width"
              min="1"
              max="20"
              step="0.5"
              value={parameters.width}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="height">Domain Height:</label>
            <input
              type="number"
              id="height"
              name="height"
              min="1"
              max="20"
              step="0.5"
              value={parameters.height}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="mesh_density">Mesh Density:</label>
            <input
              type="range"
              id="mesh_density"
              name="mesh_density"
              min="0.1"
              max="1"
              step="0.1"
              value={parameters.mesh_density}
              onChange={handleParameterChange}
            />
            <span>{parameters.mesh_density}</span>
          </div>
          
          <div className="parameter-group">
            <label htmlFor="mesh_quality">Mesh Quality:</label>
            <input
              type="range"
              id="mesh_quality"
              name="mesh_quality"
              min="10"
              max="50"
              step="5"
              value={parameters.mesh_quality}
              onChange={handleParameterChange}
            />
            <span>{parameters.mesh_quality}</span>
          </div>
          
          <div className="parameter-group checkbox">
            <label htmlFor="with_holes">Include Holes:</label>
            <input
              type="checkbox"
              id="with_holes"
              name="with_holes"
              checked={parameters.with_holes}
              onChange={handleParameterChange}
            />
          </div>
          
          {parameters.with_holes && (
            <>
              <div className="parameter-group">
                <label htmlFor="hole_rows">Hole Rows:</label>
                <input
                  type="number"
                  id="hole_rows"
                  name="hole_rows"
                  min="1"
                  max="5"
                  step="1"
                  value={parameters.hole_rows}
                  onChange={handleParameterChange}
                />
              </div>
              
              <div className="parameter-group">
                <label htmlFor="hole_cols">Hole Columns:</label>
                <input
                  type="number"
                  id="hole_cols"
                  name="hole_cols"
                  min="1"
                  max="5"
                  step="1"
                  value={parameters.hole_cols}
                  onChange={handleParameterChange}
                />
              </div>
              
              <div className="parameter-group">
                <label htmlFor="hole_radius">Hole Radius:</label>
                <input
                  type="number"
                  id="hole_radius"
                  name="hole_radius"
                  min="0.1"
                  max="1"
                  step="0.1"
                  value={parameters.hole_radius}
                  onChange={handleParameterChange}
                />
              </div>
            </>
          )}
          
          <div className="parameter-group">
            <label htmlFor="bottom_value">Bottom Temperature:</label>
            <input
              type="number"
              id="bottom_value"
              name="bottom_value"
              step="10"
              value={parameters.bottom_value}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="top_value">Top Temperature:</label>
            <input
              type="number"
              id="top_value"
              name="top_value"
              step="10"
              value={parameters.top_value}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="left_value">Left Temperature:</label>
            <input
              type="number"
              id="left_value"
              name="left_value"
              step="10"
              value={parameters.left_value}
              onChange={handleParameterChange}
            />
          </div>
          
          <div className="parameter-group">
            <label htmlFor="right_value">Right Temperature:</label>
            <input
              type="number"
              id="right_value"
              name="right_value"
              step="10"
              value={parameters.right_value}
              onChange={handleParameterChange}
            />
          </div>
        </div>
      );
    }
  };

  // Function to render results for 1D heat and wave equations
  const renderHeatWaveResults = () => {
    if (!results || !results.x || !results.u || !results.t) {
      return null;
    }
    
    return (
      <div className="results-container">
        <h3>Results</h3>
        
        {/* Animation controls */}
        <div className="animation-controls">
          <label htmlFor="time-slider">Time: {selectedTime?.toFixed(4)}</label>
          <input
            type="range"
            id="time-slider"
            min="0"
            max={availableTimes.length - 1}
            value={availableTimes.indexOf(selectedTime)}
            onChange={(e) => setSelectedTime(availableTimes[parseInt(e.target.value)])}
          />
        </div>
        
        {/* Main plot */}
        {results.plots && results.plots.animation && (
          <div className="plot-container">
            <img src={`data:image/png;base64,${results.plots.animation}`} alt="Solution at selected time" />
          </div>
        )}
        
        {/* Individual plots */}
        {showIndividualPlots && results.plots && results.plots.individual && (
          <div className="individual-plots">
            <h4>Solution at Different Times</h4>
            <img src={`data:image/png;base64,${results.plots.individual}`} alt="Solutions at different times" />
          </div>
        )}
      </div>
    );
  };

  // Function to render results for Burgers equation
  const renderBurgersResults = () => {
    if (!results || !results.plots) {
      return null;
    }
    
    return (
      <div className="results-container">
        <h3>Burgers Equation Results</h3>
        
        {/* Waterfall plot */}
        {results.plots.waterfall && (
          <div className="plot-container">
            <h4>Waterfall Plot</h4>
            <img src={`data:image/png;base64,${results.plots.waterfall}`} alt="Waterfall plot" />
          </div>
        )}
        
        {/* Animation */}
        {results.plots.animation && (
          <div className="plot-container">
            <h4>Animation</h4>
            <img src={`data:image/png;base64,${results.plots.animation}`} alt="Animation" />
          </div>
        )}
        
        {/* Individual plots */}
        {results.plots.individual && (
          <div className="individual-plots">
            <h4>Solution at Different Times</h4>
            <img src={`data:image/png;base64,${results.plots.individual}`} alt="Solutions at different times" />
          </div>
        )}
      </div>
    );
  };

  // Function to render results for 2D heat equation
  const render2DResults = () => {
    if (!results || !results.plots) {
      return null;
    }
    
    return (
      <div className="results-container">
        <h3>2D Heat Equation Results</h3>
        
        {/* Mesh plot */}
        {results.plots.mesh && (
          <div className="plot-container">
            <h4>Mesh</h4>
            <img src={`data:image/png;base64,${results.plots.mesh}`} alt="Mesh" />
          </div>
        )}
        
        {/* Solution plot */}
        {results.plots.solution && (
          <div className="plot-container">
            <h4>Temperature Distribution</h4>
            <img src={`data:image/png;base64,${results.plots.solution}`} alt="Temperature distribution" />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CalcDynamics: Differential Equation Solver</h1>
        <div className="tabs">
          <button 
            className={activeTab === 'equations' ? 'active' : ''} 
            onClick={() => handleTabChange('equations')}
          >
            Equations
          </button>
          <button 
            className={activeTab === 'about' ? 'active' : ''} 
            onClick={() => handleTabChange('about')}
          >
            About
          </button>
        </div>
      </header>
      
      <main>
        {activeTab === 'equations' ? (
          <div className="equation-solver">
            <div className="controls">
              <div className="dimension-selector">
                <label>Dimension:</label>
                <div className="radio-group">
                  <label>
                    <input
                      type="radio"
                      name="dimension"
                      value="1D"
                      checked={dimension === '1D'}
                      onChange={handleDimensionChange}
                    />
                    1D
                  </label>
                  <label>
                    <input
                      type="radio"
                      name="dimension"
                      value="2D"
                      checked={dimension === '2D'}
                      onChange={handleDimensionChange}
                    />
                    2D
                  </label>
                </div>
              </div>
              
              {dimension === '1D' && (
                <div className="equation-type-selector">
                  <label>Equation Type:</label>
                  <div className="radio-group">
                    <label>
                      <input
                        type="radio"
                        name="equationType"
                        value="heat"
                        checked={equationType === 'heat'}
                        onChange={handleEquationTypeChange}
                      />
                      Heat
                    </label>
                    <label>
                      <input
                        type="radio"
                        name="equationType"
                        value="wave"
                        checked={equationType === 'wave'}
                        onChange={handleEquationTypeChange}
                      />
                      Wave
                    </label>
                    <label>
                      <input
                        type="radio"
                        name="equationType"
                        value="burgers"
                        checked={equationType === 'burgers'}
                        onChange={handleEquationTypeChange}
                      />
                      Burgers
                    </label>
                  </div>
                </div>
              )}
            </div>
            
            <form onSubmit={handleSubmit}>
              {renderEquationParameters()}
              
              <div className="form-actions">
                <button type="submit" disabled={loading}>
                  {loading ? 'Solving...' : 'Solve Equation'}
                </button>
              </div>
              
              {loading && (
                <div className="loading-indicator">
                  <p>Solving equation... This may take a few moments.</p>
                  <div className="spinner"></div>
                </div>
              )}
              
              {error && (
                <div className="error-message">
                  <h3>Error</h3>
                  <p>{error}</p>
                  <p>Troubleshooting tips:</p>
                  <ul>
                    <li>Check your internet connection</li>
                    <li>Try reducing the complexity (use fewer grid points)</li>
                    <li>Refresh the page and try again</li>
                  </ul>
                </div>
              )}
            </form>
            
            {dimension === '1D' && equationType !== 'burgers' && results && renderHeatWaveResults()}
            {dimension === '1D' && equationType === 'burgers' && results && renderBurgersResults()}
            {dimension === '2D' && results && render2DResults()}
          </div>
        ) : (
          <div className="about-page">
            {/* About page content */}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

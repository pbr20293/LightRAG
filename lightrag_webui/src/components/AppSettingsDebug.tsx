// Debug version of AppSettings to help troubleshoot
import { useState } from 'react'

export default function AppSettingsDebug() {
  const [opened, setOpened] = useState(false)
  
  return (
    <div>
      <button onClick={() => setOpened(!opened)}>Debug Settings</button>
      {opened && (
        <div style={{ border: '1px solid red', padding: '10px', margin: '10px' }}>
          <h3>Debug Settings Panel</h3>
          <div>
            <label>
              <input type="checkbox" />
              Engineering Prompts Toggle
            </label>
          </div>
          <div>Entity Types: person, organization, location...</div>
        </div>
      )}
    </div>
  )
}
import React from 'react';
import clsx from 'clsx';
import styles from './IsaacDiagram.module.css';

// Simple SVG diagram component for Isaac architecture
const IsaacArchitectureDiagram = ({ title, description, type }) => {
  return (
    <div className={clsx('margin--md', styles.isaacDiagramContainer)}>
      <div className={styles.isaacDiagram}>
        <h4 className={styles.diagramTitle}>{title}</h4>
        <div className={styles.diagramDescription}>{description}</div>
        <div className={styles.svgContainer}>
          {type === 'isaac-sim' && (
            <svg width="400" height="200" viewBox="0 0 400 200" className={styles.diagramSvg}>
              {/* Isaac Sim Architecture */}
              <rect x="50" y="50" width="300" height="100" rx="10" fill="#e1f5fe" stroke="#0277bd" strokeWidth="2"/>
              <text x="200" y="75" textAnchor="middle" className={styles.svgText}>Isaac Sim</text>
              <text x="200" y="95" textAnchor="middle" className={styles.svgText}>Simulation Environment</text>

              <rect x="100" y="130" width="80" height="40" rx="5" fill="#e8f5e8" stroke="#388e3c" strokeWidth="1"/>
              <text x="140" y="155" textAnchor="middle" fontSize="12" className={styles.svgText}>Physics</text>

              <rect x="190" y="130" width="80" height="40" rx="5" fill="#e8f5e8" stroke="#388e3c" strokeWidth="1"/>
              <text x="230" y="155" textAnchor="middle" fontSize="12" className={styles.svgText}>Rendering</text>

              <rect x="280" y="130" width="80" height="40" rx="5" fill="#e8f5e8" stroke="#388e3c" strokeWidth="1"/>
              <text x="320" y="155" textAnchor="middle" fontSize="12" className={styles.svgText}>Sensors</text>

              <line x1="200" y1="100" x2="200" y2="130" stroke="#757575" strokeWidth="2" strokeDasharray="5,5"/>
            </svg>
          )}

          {type === 'isaac-ros' && (
            <svg width="400" height="250" viewBox="0 0 400 250" className={styles.diagramSvg}>
              {/* Isaac ROS Pipeline */}
              <rect x="20" y="20" width="360" height="210" rx="10" fill="#fff3e0" stroke="#ef6c00" strokeWidth="2"/>
              <text x="200" y="45" textAnchor="middle" className={styles.svgText}>Isaac ROS Pipeline</text>

              <rect x="50" y="80" width="60" height="40" rx="5" fill="#e3f2fd" stroke="#1976d2" strokeWidth="1"/>
              <text x="80" y="105" textAnchor="middle" fontSize="10" className={styles.svgText}>Camera</text>

              <rect x="130" y="80" width="60" height="40" rx="5" fill="#e8f5e8" stroke="#388e3c" strokeWidth="1"/>
              <text x="160" y="105" textAnchor="middle" fontSize="10" className={styles.svgText}>VSLAM</text>

              <rect x="210" y="80" width="60" height="40" rx="5" fill="#f3e5f5" stroke="#7b1fa2" strokeWidth="1"/>
              <text x="240" y="105" textAnchor="middle" fontSize="10" className={styles.svgText}>Perception</text>

              <rect x="290" y="80" width="60" height="40" rx="5" fill="#ffebee" stroke="#d32f2f" strokeWidth="1"/>
              <text x="320" y="105" textAnchor="middle" fontSize="10" className={styles.svgText}>AI/ML</text>

              <line x1="110" y1="100" x2="130" y2="100" stroke="#757575" strokeWidth="2" markerEnd="url(#arrowhead)"/>
              <line x1="190" y1="100" x2="210" y2="100" stroke="#757575" strokeWidth="2" markerEnd="url(#arrowhead)"/>
              <line x1="270" y1="100" x2="290" y2="100" stroke="#757575" strokeWidth="2" markerEnd="url(#arrowhead)"/>

              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#757575" />
                </marker>
              </defs>
            </svg>
          )}

          {type === 'nav2' && (
            <svg width="400" height="250" viewBox="0 0 400 250" className={styles.diagramSvg}>
              {/* Nav2 Architecture */}
              <rect x="20" y="20" width="360" height="210" rx="10" fill="#f1f8e9" stroke="#689f38" strokeWidth="2"/>
              <text x="200" y="45" textAnchor="middle" className={styles.svgText}>Nav2 for Humanoid Robots</text>

              <rect x="50" y="70" width="80" height="40" rx="5" fill="#e3f2fd" stroke="#1976d2" strokeWidth="1"/>
              <text x="90" y="95" textAnchor="middle" fontSize="10" className={styles.svgText}>Localizer</text>

              <rect x="150" y="70" width="80" height="40" rx="5" fill="#e8f5e8" stroke="#388e3c" strokeWidth="1"/>
              <text x="190" y="95" textAnchor="middle" fontSize="10" className={styles.svgText}>Mapper</text>

              <rect x="250" y="70" width="80" height="40" rx="5" fill="#f3e5f5" stroke="#7b1fa2" strokeWidth="1"/>
              <text x="290" y="95" textAnchor="middle" fontSize="10" className={styles.svgText}>Planner</text>

              <rect x="100" y="140" width="80" height="40" rx="5" fill="#fff3e0" stroke="#ef6c00" strokeWidth="1"/>
              <text x="140" y="165" textAnchor="middle" fontSize="10" className={styles.svgText}>Controller</text>

              <rect x="220" y="140" width="80" height="40" rx="5" fill="#e0f2f1" stroke="#00695c" strokeWidth="1"/>
              <text x="260" y="165" textAnchor="middle" fontSize="10" className={styles.svgText}>Recovery</text>

              <line x1="130" y1="110" x2="150" y2="140" stroke="#757575" strokeWidth="2" markerEnd="url(#arrowhead)"/>
              <line x1="230" y1="110" x2="220" y2="140" stroke="#757575" strokeWidth="2" markerEnd="url(#arrowhead)"/>

              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#757575" />
                </marker>
              </defs>
            </svg>
          )}
        </div>
      </div>
    </div>
  );
};

export default function IsaacDiagram({ title, description, type = 'isaac-sim' }) {
  return <IsaacArchitectureDiagram title={title} description={description} type={type} />;
}
import React from 'react';
import styles from './SimulationDiagram.module.css';

// A simple simulation diagram component to visualize digital twin concepts
const SimulationDiagram = ({ title, description, type = 'gazebo' }) => {
  const diagramClass = `${styles.diagram} ${styles[type]}`;

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>{title}</h3>
      <div className={diagramClass}>
        <div className={styles.element}>Physical Robot</div>
        <div className={styles.arrow}>↔</div>
        <div className={styles.element}>Digital Twin</div>
        <div className={styles.connection}>
          <div className={styles.sensor}>Sensors</div>
          <div className={styles.physics}>Physics</div>
          <div className={styles.visual}>Visual</div>
        </div>
      </div>
      <p className={styles.description}>{description}</p>
    </div>
  );
};

export default SimulationDiagram;
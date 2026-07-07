import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Icosahedron, Points, PointMaterial } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';

interface TechNodeSphereProps {
  volumeLevel: number; // 0 to 1
}

export const TechNodeSphere: React.FC<TechNodeSphereProps> = ({ volumeLevel }) => {
  const innerMeshRef = useRef<THREE.Mesh>(null!);
  const outerWireframeRef = useRef<THREE.Mesh>(null!);
  const particlesRef = useRef<THREE.Points>(null!);
  const materialRef = useRef<THREE.MeshPhysicalMaterial>(null!);
  const wireMaterialRef = useRef<THREE.MeshBasicMaterial>(null!);

  // Colors for transition
  const colorGreen = useMemo(() => new THREE.Color(0x00ff88), []);
  const colorYellow = useMemo(() => new THREE.Color(0xffff00), []);
  const colorRed = useMemo(() => new THREE.Color(0xff0055), []);

  // Generate random particles around the sphere
  const particlesCount = 200;
  const positions = useMemo(() => {
    const pos = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount; i++) {
      const radius = 2.5 + Math.random() * 2;
      const theta = Math.random() * 2 * Math.PI;
      const phi = Math.acos(Math.random() * 2 - 1);
      pos[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = radius * Math.cos(phi);
    }
    return pos;
  }, [particlesCount]);

  useFrame((_, delta) => {
    const smoothVolume = volumeLevel; // Can add easing if needed
    
    // Scale based on volume
    const targetScale = 1 + smoothVolume * 1.5;
    innerMeshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
    outerWireframeRef.current.scale.lerp(new THREE.Vector3(targetScale * 1.1, targetScale * 1.1, targetScale * 1.1), 0.1);
    
    // Rotation speed based on volume
    const baseRotationSpeed = 0.2;
    const dynamicRotationSpeed = baseRotationSpeed + smoothVolume * 2;
    innerMeshRef.current.rotation.y += delta * dynamicRotationSpeed;
    innerMeshRef.current.rotation.x += delta * (dynamicRotationSpeed * 0.5);
    outerWireframeRef.current.rotation.y -= delta * (dynamicRotationSpeed * 0.8);
    particlesRef.current.rotation.y += delta * (baseRotationSpeed * 0.5);

    // Roughness and transmission reaction
    if (materialRef.current) {
      materialRef.current.roughness = THREE.MathUtils.lerp(materialRef.current.roughness, 0.1 + smoothVolume * 0.5, 0.1);
      materialRef.current.transmission = THREE.MathUtils.lerp(materialRef.current.transmission, 0.9 - smoothVolume * 0.4, 0.1);
    }

    // Color transition (Green -> Yellow -> Red)
    let targetColor = colorGreen;
    if (smoothVolume > 0.6) {
      targetColor = colorYellow.clone().lerp(colorRed, (smoothVolume - 0.6) * 2.5);
    } else if (smoothVolume > 0.2) {
      targetColor = colorGreen.clone().lerp(colorYellow, (smoothVolume - 0.2) * 2.5);
    }

    if (materialRef.current) {
      materialRef.current.color.lerp(targetColor, 0.1);
      materialRef.current.emissive.lerp(targetColor, 0.1);
      materialRef.current.emissiveIntensity = THREE.MathUtils.lerp(materialRef.current.emissiveIntensity, smoothVolume * 2, 0.1);
    }
    if (wireMaterialRef.current) {
      wireMaterialRef.current.color.lerp(targetColor, 0.1);
    }
  });

  return (
    <>
      <ambientLight intensity={0.2} />
      <directionalLight position={[5, 5, 5]} intensity={1} />
      
      {/* Inner physical glass-like sphere */}
      <Icosahedron ref={innerMeshRef} args={[1, 3]} position={[0, 0, 0]}>
        <meshPhysicalMaterial 
          ref={materialRef}
          transmission={0.9}
          opacity={1}
          metalness={0.2}
          roughness={0.1}
          ior={1.5}
          thickness={0.5}
          color={0x00ff88}
          emissive={0x00ff88}
          emissiveIntensity={0}
        />
      </Icosahedron>

      {/* Outer wireframe */}
      <Icosahedron ref={outerWireframeRef} args={[1, 1]} position={[0, 0, 0]}>
        <meshBasicMaterial 
          ref={wireMaterialRef}
          wireframe 
          color={0x00ff88} 
          transparent
          opacity={0.3}
        />
      </Icosahedron>

      {/* Orbiting Particles */}
      <Points ref={particlesRef} positions={positions}>
        <PointMaterial
          transparent
          color={0xffffff}
          size={0.05}
          sizeAttenuation={true}
          depthWrite={false}
          opacity={0.6}
        />
      </Points>

      <EffectComposer>
        <Bloom 
          luminanceThreshold={0.2}
          luminanceSmoothing={0.9}
          intensity={1.5}
        />
      </EffectComposer>
    </>
  );
};

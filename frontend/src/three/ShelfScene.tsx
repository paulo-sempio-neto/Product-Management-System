import { RoundedBox } from "@react-three/drei";
import { Canvas, useFrame, useThree, type ThreeEvent } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

/**
 * Hero scene for the auth screen: products drop onto a store shelf
 * ("gôndola"), bounce with squash-and-stretch and get a price tag.
 * Pointer moves tilt the shelf; clicking a product makes it hop.
 */

type Kind = "box" | "tall" | "can" | "jar";

type Item = {
  kind: Kind;
  shelf: 0 | 1;
  x: number;
  color: string;
  band: string;
  price: string;
  delay: number;
};

const SHELF_Y = [-0.15, 2.05] as const;
const SHELF_WIDTH = 8.6;

const ITEMS: Item[] = [
  { kind: "tall", shelf: 1, x: -2.8, color: "#ffd23f", band: "#0e1530", price: "R$ 12,90", delay: 0.15 },
  { kind: "can", shelf: 1, x: -1.55, color: "#ff5a5f", band: "#ffffff", price: "R$ 4,49", delay: 0.32 },
  { kind: "can", shelf: 1, x: -0.75, color: "#ff5a5f", band: "#ffffff", price: "R$ 4,49", delay: 0.42 },
  { kind: "box", shelf: 1, x: 0.55, color: "#ffffff", band: "#2b4bff", price: "R$ 8,75", delay: 0.55 },
  { kind: "jar", shelf: 1, x: 1.95, color: "#12b886", band: "#ffffff", price: "R$ 15,30", delay: 0.7 },
  { kind: "tall", shelf: 1, x: 2.95, color: "#0e1530", band: "#ffd23f", price: "R$ 22,00", delay: 0.82 },
  { kind: "box", shelf: 0, x: -2.6, color: "#12b886", band: "#0e1530", price: "R$ 6,20", delay: 0.95 },
  { kind: "jar", shelf: 0, x: -1.2, color: "#ffffff", band: "#ff5a5f", price: "R$ 9,99", delay: 1.08 },
  { kind: "tall", shelf: 0, x: 0.05, color: "#ffd23f", band: "#2b4bff", price: "R$ 18,40", delay: 1.2 },
  { kind: "can", shelf: 0, x: 1.25, color: "#0e1530", band: "#ffd23f", price: "R$ 3,79", delay: 1.3 },
  { kind: "box", shelf: 0, x: 2.6, color: "#ff5a5f", band: "#ffffff", price: "R$ 11,50", delay: 1.42 },
];

const HEIGHT: Record<Kind, number> = { box: 1.05, tall: 1.75, can: 0.95, jar: 1.15 };

function usePrefersReducedMotion() {
  const [reduced] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );
  return reduced;
}

function makeTagTexture(price: string) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 112;
  const ctx = canvas.getContext("2d")!;
  ctx.fillStyle = "#ffd23f";
  ctx.beginPath();
  ctx.roundRect(0, 0, 256, 112, 14);
  ctx.fill();
  ctx.fillStyle = "#3d2e00";
  ctx.font = '700 54px "Instrument Sans Variable", "Instrument Sans", system-ui, sans-serif';
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(price, 128, 60);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

function ProductBody({ item }: { item: Item }) {
  const h = HEIGHT[item.kind];
  const material = { roughness: 0.42, metalness: 0.02 };

  if (item.kind === "can") {
    return (
      <group>
        <mesh castShadow position={[0, h / 2, 0]}>
          <cylinderGeometry args={[0.36, 0.36, h, 40]} />
          <meshStandardMaterial color={item.color} {...material} />
        </mesh>
        <mesh position={[0, h * 0.52, 0]}>
          <cylinderGeometry args={[0.365, 0.365, h * 0.3, 40]} />
          <meshStandardMaterial color={item.band} {...material} />
        </mesh>
        <mesh position={[0, h + 0.015, 0]}>
          <cylinderGeometry args={[0.3, 0.33, 0.04, 40]} />
          <meshStandardMaterial color="#c3cbdc" metalness={0.6} roughness={0.3} />
        </mesh>
      </group>
    );
  }

  if (item.kind === "jar") {
    return (
      <group>
        <mesh castShadow position={[0, h * 0.42, 0]}>
          <cylinderGeometry args={[0.42, 0.42, h * 0.84, 40]} />
          <meshStandardMaterial color={item.color} {...material} />
        </mesh>
        <mesh castShadow position={[0, h * 0.92, 0]}>
          <cylinderGeometry args={[0.34, 0.34, h * 0.16, 40]} />
          <meshStandardMaterial color={item.band} {...material} />
        </mesh>
        <mesh position={[0, h * 0.42, 0]}>
          <cylinderGeometry args={[0.425, 0.425, h * 0.28, 40]} />
          <meshStandardMaterial color={item.band} {...material} />
        </mesh>
      </group>
    );
  }

  const w = item.kind === "tall" ? 0.82 : 1.05;
  return (
    <group>
      <RoundedBox castShadow args={[w, h, 0.6]} radius={0.06} smoothness={4} position={[0, h / 2, 0]}>
        <meshStandardMaterial color={item.color} {...material} />
      </RoundedBox>
      <mesh position={[0, h * 0.55, 0.302]}>
        <planeGeometry args={[w * 0.72, h * 0.22]} />
        <meshStandardMaterial color={item.band} {...material} />
      </mesh>
    </group>
  );
}

function Product({ item, reduced, tag }: { item: Item; reduced: boolean; tag: THREE.Texture | null }) {
  const group = useRef<THREE.Group>(null);
  const body = useRef<THREE.Group>(null);
  const restY = SHELF_Y[item.shelf] + 0.09;
  const sim = useRef({
    y: reduced ? restY : restY + 7 + item.shelf * 1.5,
    vy: 0,
    squash: 0,
    spin: 0,
    started: reduced,
    elapsed: 0,
  });

  const hop = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    if (reduced) return;
    const s = sim.current;
    if (Math.abs(s.y - restY) < 0.05) {
      s.vy = 9;
      s.spin = Math.PI * 2;
    }
  };

  useFrame((_, rawDelta) => {
    const delta = Math.min(rawDelta, 1 / 30);
    const s = sim.current;
    s.elapsed += delta;
    if (!s.started && s.elapsed >= item.delay) s.started = true;

    if (s.started && !reduced) {
      s.vy -= 32 * delta;
      s.y += s.vy * delta;
      if (s.y <= restY) {
        s.y = restY;
        if (Math.abs(s.vy) > 1.2) {
          s.squash = Math.min(0.28, Math.abs(s.vy) * 0.022);
          s.vy = -s.vy * 0.32;
        } else {
          s.vy = 0;
        }
      }
      s.squash *= Math.pow(0.0008, delta);
      s.spin *= Math.pow(0.004, delta);
    }

    if (group.current) group.current.position.y = s.y;
    if (body.current) {
      body.current.scale.set(1 + s.squash * 0.55, 1 - s.squash, 1 + s.squash * 0.55);
      body.current.rotation.y = s.spin;
    }
  });

  return (
    <group position={[item.x, 0, 0]}>
      <group ref={group} onClick={hop} onPointerOver={() => (document.body.style.cursor = "pointer")} onPointerOut={() => (document.body.style.cursor = "")}>
        <group ref={body}>
          <ProductBody item={item} />
        </group>
      </group>
      {tag && (
        <mesh position={[0, SHELF_Y[item.shelf] - 0.02, 0.87]}>
          <planeGeometry args={[0.78, 0.34]} />
          <meshBasicMaterial map={tag} transparent toneMapped={false} />
        </mesh>
      )}
    </group>
  );
}

function Shelf({ y }: { y: number }) {
  return (
    <group position={[0, y, 0]}>
      <RoundedBox receiveShadow castShadow args={[SHELF_WIDTH, 0.18, 1.6]} radius={0.05} smoothness={3}>
        <meshStandardMaterial color="#f6f8fb" roughness={0.6} />
      </RoundedBox>
      <mesh position={[0, -0.02, 0.81]}>
        <boxGeometry args={[SHELF_WIDTH, 0.3, 0.06]} />
        <meshStandardMaterial color="#d8deea" roughness={0.5} />
      </mesh>
    </group>
  );
}

/** Keeps the whole shelf in frame for any viewport aspect ratio. */
function FitCamera() {
  const { camera, size } = useThree();
  useEffect(() => {
    const perspective = camera as THREE.PerspectiveCamera;
    const halfFov = THREE.MathUtils.degToRad(perspective.fov / 2);
    const aspect = size.width / size.height;
    const fitHeight = 5.6 / (2 * Math.tan(halfFov));
    const fitWidth = 8.9 / (2 * Math.tan(halfFov) * aspect);
    perspective.position.set(0, 1.9, Math.max(fitHeight, fitWidth) + 0.8);
    perspective.lookAt(0, 1.75, 0);
    perspective.updateProjectionMatrix();
  }, [camera, size]);
  return null;
}

function Rig({ children, reduced }: { children: React.ReactNode; reduced: boolean }) {
  const group = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame((state, delta) => {
    if (!group.current || reduced) return;
    const idle = Math.sin(state.clock.elapsedTime * 0.4) * 0.03;
    const targetY = pointer.x * 0.22 + idle - 0.12;
    const targetX = -pointer.y * 0.08 + 0.06;
    group.current.rotation.y = THREE.MathUtils.damp(group.current.rotation.y, targetY, 3, delta);
    group.current.rotation.x = THREE.MathUtils.damp(group.current.rotation.x, targetX, 3, delta);
  });
  return (
    <group ref={group} rotation={[0.06, -0.12, 0]}>
      {children}
    </group>
  );
}

function SceneContents() {
  const reduced = usePrefersReducedMotion();
  const [tags, setTags] = useState<Map<string, THREE.Texture> | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fontReady = document.fonts
      ? document.fonts.load('700 54px "Instrument Sans Variable"').catch(() => undefined)
      : Promise.resolve();
    void fontReady.then(() => {
      if (cancelled) return;
      const map = new Map<string, THREE.Texture>();
      ITEMS.forEach((item) => {
        if (!map.has(item.price)) map.set(item.price, makeTagTexture(item.price));
      });
      setTags(map);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => () => tags?.forEach((texture) => texture.dispose()), [tags]);

  const shadowPlane = useMemo(() => new THREE.ShadowMaterial({ opacity: 0.14 }), []);

  return (
    <>
      <ambientLight intensity={1.1} />
      <hemisphereLight args={["#ffffff", "#2b4bff", 0.7]} />
      <directionalLight
        castShadow
        position={[4, 7, 6]}
        intensity={2.2}
        shadow-mapSize={[1024, 1024]}
        shadow-camera-left={-6}
        shadow-camera-right={6}
        shadow-camera-top={6}
        shadow-camera-bottom={-6}
        shadow-bias={-0.0005}
      />
      <FitCamera />
      <directionalLight position={[-5, 2, 4]} intensity={0.6} color="#dfe5ff" />
      <Rig reduced={reduced}>
        <Shelf y={SHELF_Y[0]} />
        <Shelf y={SHELF_Y[1]} />
        {ITEMS.map((item, index) => (
          <Product key={index} item={item} reduced={reduced} tag={tags?.get(item.price) ?? null} />
        ))}
        <mesh receiveShadow position={[0, 0, -0.85]} material={shadowPlane}>
          <planeGeometry args={[20, 14]} />
        </mesh>
      </Rig>
    </>
  );
}

export default function ShelfScene() {
  const wrapper = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(true);

  // Stop rendering when the stage scrolls out of view (saves battery on phones).
  useEffect(() => {
    const node = wrapper.current;
    if (!node || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), { threshold: 0.05 });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={wrapper} className="shelf-wrapper">
    <Canvas
      className="shelf-canvas"
      frameloop={visible ? "always" : "never"}
      shadows
      dpr={[1, 2]}
      camera={{ position: [0, 0.6, 15], fov: 34 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      aria-hidden="true"
    >
      <SceneContents />
    </Canvas>
    </div>
  );
}

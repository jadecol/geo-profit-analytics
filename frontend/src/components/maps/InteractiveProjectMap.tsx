import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix para iconos de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface InteractiveProjectMapProps {
  projectLocation: string;
  projectData?: {
    name: string;
    coordinates?: [number, number];
    totalArea: number;
    terrainValue: number;
  };
  analysisData?: {
    locationScore: number;
    accessibilityScore: number;
    riskFactors: string[];
    nearbyServices: string[];
  };
  onLocationSelect?: (lat: number, lng: number, address: string) => void;
}

const InteractiveProjectMap: React.FC<InteractiveProjectMapProps> = ({
  projectLocation,
  projectData,
  analysisData,
  onLocationSelect
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<[number, number] | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Coordenadas por defecto para Colombia
  const defaultCoords: [number, number] = [4.7110, -74.0721]; // Bogotá
  const projectCoords = projectData?.coordinates || defaultCoords;

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Inicializar mapa con estilo futurista
    const map = L.map(mapRef.current, {
      center: projectCoords,
      zoom: 13,
      zoomControl: false,
      attributionControl: false
    });

    // Agregar control de zoom personalizado
    L.control.zoom({ position: 'topright' }).addTo(map);

    // Tile layer con estilo oscuro futurista
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© CartoDB',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(map);

    // Crear marcador personalizado para el proyecto
    const projectIcon = L.divIcon({
      html: `
        <div style="
          width: 30px;
          height: 30px;
          background: linear-gradient(135deg, #00ff88, #00cc66);
          border-radius: 50%;
          border: 3px solid #ffffff;
          box-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          animation: pulse 2s infinite;
        ">
          <div style="
            width: 10px;
            height: 10px;
            background: #ffffff;
            border-radius: 50%;
          "></div>
        </div>
        <style>
          @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(0, 255, 136, 0.8); }
            50% { transform: scale(1.1); box-shadow: 0 0 30px rgba(0, 255, 136, 1); }
            100% { transform: scale(1); box-shadow: 0 0 20px rgba(0, 255, 136, 0.8); }
          }
        </style>
      `,
      className: 'project-marker',
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });

    const projectMarker = L.marker(projectCoords, { icon: projectIcon }).addTo(map);
    
    // Popup del proyecto con información
    const popupContent = `
      <div style="
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(20, 20, 40, 0.95));
        color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 136, 0.3);
        min-width: 200px;
      ">
        <h3 style="margin: 0 0 10px 0; color: #00ff88; font-size: 16px;">
          ${projectData?.name || 'Proyecto'}
        </h3>
        <p style="margin: 5px 0; font-size: 12px;">📍 ${projectLocation}</p>
        ${projectData?.totalArea ? `<p style="margin: 5px 0; font-size: 12px;">📐 ${projectData.totalArea.toLocaleString()} m²</p>` : ''}
        ${projectData?.terrainValue ? `<p style="margin: 5px 0; font-size: 12px;">💰 $${projectData.terrainValue.toLocaleString()}</p>` : ''}
        ${analysisData ? `
          <hr style="border: 1px solid rgba(0, 255, 136, 0.3); margin: 10px 0;">
          <p style="margin: 5px 0; font-size: 12px;">📊 Ubicación: ${analysisData.locationScore}/10</p>
          <p style="margin: 5px 0; font-size: 12px;">🚗 Accesibilidad: ${analysisData.accessibilityScore}/10</p>
        ` : ''}
      </div>
    `;

    projectMarker.bindPopup(popupContent);

    // Agregar servicios cercanos si existen
    if (analysisData?.nearbyServices) {
      analysisData.nearbyServices.forEach((service, index) => {
        // Generar coordenadas aproximadas alrededor del proyecto
        const offset = 0.01;
        const angle = (index * 60) * (Math.PI / 180);
        const lat = projectCoords[0] + Math.cos(angle) * offset;
        const lng = projectCoords[1] + Math.sin(angle) * offset;

        const serviceIcon = L.divIcon({
          html: `
            <div style="
              width: 20px;
              height: 20px;
              background: rgba(0, 136, 255, 0.8);
              border-radius: 50%;
              border: 2px solid #ffffff;
              box-shadow: 0 0 10px rgba(0, 136, 255, 0.6);
            "></div>
          `,
          className: 'service-marker',
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        });

        L.marker([lat, lng], { icon: serviceIcon })
          .addTo(map)
          .bindPopup(`
            <div style="
              background: linear-gradient(135deg, rgba(0, 136, 255, 0.9), rgba(0, 100, 200, 0.95));
              color: white;
              padding: 10px;
              border-radius: 8px;
              border: 1px solid rgba(0, 136, 255, 0.5);
            ">
              <strong style="color: #88ccff;">${service}</strong>
            </div>
          `);
      });
    }

    // Click handler para seleccionar nueva ubicación
    if (onLocationSelect) {
      map.on('click', async (e) => {
        const { lat, lng } = e.latlng;
        setSelectedPoint([lat, lng]);
        
        // Geocodificación inversa simulada
        const address = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
        onLocationSelect(lat, lng, address);

        // Agregar marcador temporal
        const tempMarker = L.marker([lat, lng], {
          icon: L.divIcon({
            html: `
              <div style="
                width: 25px;
                height: 25px;
                background: rgba(255, 136, 0, 0.8);
                border-radius: 50%;
                border: 2px solid #ffffff;
                box-shadow: 0 0 15px rgba(255, 136, 0, 0.8);
                animation: bounce 1s infinite;
              "></div>
              <style>
                @keyframes bounce {
                  0%, 100% { transform: translateY(0); }
                  50% { transform: translateY(-10px); }
                }
              </style>
            `,
            iconSize: [25, 25],
            iconAnchor: [12, 12]
          })
        }).addTo(map);

        // Remover marcador temporal después de 3 segundos
        setTimeout(() => {
          map.removeLayer(tempMarker);
        }, 3000);
      });
    }

    mapInstanceRef.current = map;
    setMapLoaded(true);

    // Cleanup
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [projectLocation, projectData, analysisData, onLocationSelect]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      style={{
        background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(20, 20, 40, 0.9))',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(0, 255, 136, 0.3)',
        borderRadius: '20px',
        padding: '20px',
        margin: '20px 0',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Header del mapa */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{
          marginBottom: '15px',
          textAlign: 'center'
        }}
      >
        <h3 style={{
          color: '#00ff88',
          fontSize: '18px',
          fontWeight: '300',
          margin: '0 0 5px 0',
          textShadow: '0 0 10px rgba(0, 255, 136, 0.5)'
        }}>
          Análisis Geoespacial Interactivo
        </h3>
        <p style={{
          color: 'rgba(255, 255, 255, 0.7)',
          fontSize: '12px',
          margin: 0
        }}>
          {projectLocation}
        </p>
      </motion.div>

      {/* Contenedor del mapa */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: mapLoaded ? 1 : 0.5 }}
        transition={{ delay: 0.4 }}
        style={{
          height: '400px',
          borderRadius: '15px',
          overflow: 'hidden',
          border: '1px solid rgba(0, 255, 136, 0.2)',
          position: 'relative'
        }}
      >
        <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
        
        {/* Overlay de carga */}
        {!mapLoaded && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#00ff88',
            fontSize: '14px'
          }}>
            Cargando mapa interactivo...
          </div>
        )}
      </motion.div>

      {/* Panel de información lateral */}
      {analysisData && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          style={{
            marginTop: '20px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px'
          }}
        >
          <div style={{
            background: 'rgba(0, 255, 136, 0.1)',
            border: '1px solid rgba(0, 255, 136, 0.3)',
            borderRadius: '10px',
            padding: '15px'
          }}>
            <h4 style={{ color: '#00ff88', fontSize: '14px', margin: '0 0 10px 0' }}>
              Puntuación de Ubicación
            </h4>
            <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
              {analysisData.locationScore}/10
            </div>
          </div>

          <div style={{
            background: 'rgba(0, 136, 255, 0.1)',
            border: '1px solid rgba(0, 136, 255, 0.3)',
            borderRadius: '10px',
            padding: '15px'
          }}>
            <h4 style={{ color: '#0088ff', fontSize: '14px', margin: '0 0 10px 0' }}>
              Accesibilidad
            </h4>
            <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
              {analysisData.accessibilityScore}/10
            </div>
          </div>

          <div style={{
            background: 'rgba(255, 136, 0, 0.1)',
            border: '1px solid rgba(255, 136, 0, 0.3)',
            borderRadius: '10px',
            padding: '15px'
          }}>
            <h4 style={{ color: '#ff8800', fontSize: '14px', margin: '0 0 10px 0' }}>
              Servicios Cercanos
            </h4>
            <div style={{ color: 'white', fontSize: '12px' }}>
              {analysisData.nearbyServices.length} servicios identificados
            </div>
          </div>
        </motion.div>
      )}

      {/* Instrucciones */}
      {onLocationSelect && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          style={{
            marginTop: '15px',
            textAlign: 'center',
            color: 'rgba(255, 255, 255, 0.6)',
            fontSize: '12px'
          }}
        >
          Haz clic en el mapa para seleccionar una nueva ubicación
        </motion.div>
      )}
    </motion.div>
  );
};

export default InteractiveProjectMap;
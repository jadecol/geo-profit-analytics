import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix para iconos de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface ProjectMapProps {
  projectLocation: string;
  onLocationSelect?: (lat: number, lng: number) => void;
}

const ProjectMap: React.FC<ProjectMapProps> = ({ projectLocation, onLocationSelect }) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Inicializar mapa
    const map = L.map(mapRef.current).setView([4.7110, -74.0721], 10); // Bogotá como centro

    // Agregar tiles de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Geocodificación simple para la ubicación del proyecto
    if (projectLocation) {
      // Aquí implementarías geocodificación real o coordenadas predefinidas
      const marker = L.marker([4.7110, -74.0721]).addTo(map);
      marker.bindPopup(`<b>Proyecto:</b><br>${projectLocation}`);
    }

    // Click handler para seleccionar ubicación
    if (onLocationSelect) {
      map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        onLocationSelect(lat, lng);
        
        // Agregar marcador en la ubicación seleccionada
        L.marker([lat, lng]).addTo(map)
          .bindPopup(`Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`)
          .openPopup();
      });
    }

    mapInstanceRef.current = map;

    // Cleanup
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
      }
    };
  }, [projectLocation, onLocationSelect]);

  return (
    <div style={{
      marginTop: '20px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '10px',
        backgroundColor: '#f5f5f5',
        borderBottom: '1px solid #ddd'
      }}>
        <h4 style={{ margin: 0 }}>Ubicación del Proyecto</h4>
        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#666' }}>
          {projectLocation}
        </p>
      </div>
      <div 
        ref={mapRef} 
        style={{ height: '400px', width: '100%' }}
      />
    </div>
  );
};

export default ProjectMap;
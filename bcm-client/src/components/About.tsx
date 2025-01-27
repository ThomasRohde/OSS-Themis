import { useApp } from '../contexts/AppContext';
import type { Capability } from '../types/api';
import BackButton from './BackButton';
import themisLogo from '../assets/themis.png';

export default function About() {
  const { activeUsers, capabilities } = useApp();

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <BackButton />

      <h1 className="text-3xl font-bold mb-4">About Themis</h1>
      <img 
        src={themisLogo} 
        alt="Themis Logo" 
        className="w-48 mb-8 mx-auto shadow-lg rounded-lg transition-transform hover:scale-105" 
      />
      
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Overview</h2>
        <p className="text-gray-700 mb-4">
          Themis is a versatile tool for modeling and visualizing hierarchical structures of all kinds. While it excels at 
          creating Business Capability Models (BCM), it's equally powerful for organizing and managing:
        </p>
        <ul className="list-disc pl-8 space-y-2 text-gray-700 mb-4">
          <li>Mind Maps for brainstorming and organizing thoughts</li>
          <li>Taxonomies for classification systems</li>
          <li>Knowledge Hierarchies for information management</li>
        </ul>
        <p className="text-gray-700 mb-4">
          The tool enables you to create, organize, and visualize complex hierarchical relationships with ease, 
          making it valuable for both business and creative applications.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Why Themis?</h2>
        <p className="text-gray-700 mb-4">
          Themis, the Greek goddess of divine law and order, represents the perfect namesake for our application. 
          In ancient mythology, she was known for establishing order, customs, and natural law. Just as Themis brought 
          structure to the divine and mortal realms, our tool helps bring order and clarity to complex organizational 
          structures and hierarchies.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">How to Use</h2>
        <div className="space-y-4 text-gray-700">
          <p>1. <strong>Navigation:</strong> Use the burger menu in the top-left corner to access different sections of the application.</p>
          <p>2. <strong>Capability Tree:</strong> The main view shows your business capability tree. You can:</p>
          <ul className="list-disc pl-8 space-y-2">
            <li>Click on capabilities to expand/collapse them</li>
            <li>Drag and drop capabilities to reorganize them</li>
            <li>Use the context menu for additional options</li>
          </ul>
          <p>3. <strong>Collaboration:</strong> Multiple users can work on the same model simultaneously. Changes are synchronized in real-time.</p>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Active Users</h2>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 mb-2">Currently online ({activeUsers.length}):</p>
          <ul className="space-y-1">
            {activeUsers.map((user, index) => (
              <li key={index} className="text-gray-700">
                {user.nickname}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">Model Statistics</h2>
        <div className="bg-white rounded-lg shadow p-4">
          <ul className="space-y-2 text-gray-700">
            <li>
              <strong>Total Capabilities:</strong>{' '}
              {(() => {
                const countCapabilities = (caps: Capability[]): number => {
                  return caps.reduce((total, cap) => {
                    return total + 1 + (cap.children ? countCapabilities(cap.children) : 0);
                  }, 0);
                };
                return countCapabilities(capabilities);
              })()}
            </li>
            <li>
              <strong>Top-level Capabilities:</strong>{' '}
              {capabilities.length}
            </li>
            <li>
              <strong>Leaf Nodes:</strong>{' '}
              {(() => {
                const countLeafNodes = (caps: Capability[]): number => {
                  return caps.reduce((total, cap) => {
                    if (!cap.children || cap.children.length === 0) {
                      return total + 1;
                    }
                    return total + countLeafNodes(cap.children);
                  }, 0);
                };
                return countLeafNodes(capabilities);
              })()}
            </li>
            <li>
              <strong>Maximum Depth:</strong>{' '}
              {(() => {
                const getDepth = (cap: Capability): number => {
                  if (!cap.children || cap.children.length === 0) return 1;
                  return 1 + Math.max(...cap.children.map(getDepth));
                };
                
                return capabilities.length
                  ? Math.max(...capabilities.map(getDepth))
                  : 0;
              })()}
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}

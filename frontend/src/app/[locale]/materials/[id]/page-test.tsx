"use client";

import React from "react";

export default function TestMaterialPage() {
  console.log('🚨 TEST COMPONENT IS RENDERING!!!');
  
  return (
    <div style={{ 
      padding: '2rem', 
      backgroundColor: 'yellow', 
      border: '5px solid red',
      textAlign: 'center'
    }}>
      <h1 style={{ color: 'red', fontSize: '2rem' }}>
        🚨 TEST COMPONENT IS WORKING! 🚨
      </h1>
      <p>If you see this, the routing is working.</p>
      <p>Material ID from URL: demo-1</p>
    </div>
  );
}

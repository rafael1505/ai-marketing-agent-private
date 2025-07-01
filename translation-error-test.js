/**
 * Script to test translation error handling in the settings page
 * 
 * This script simulates missing translation keys to verify that our 
 * optional chaining fix prevents "Cannot read properties of undefined" errors.
 */

function testTranslationErrorHandling() {
  console.log('===== Translation Error Handling Test =====');
  
  try {
    // Get the current t object from React's internal state
    // This is a hacky way to access React state but works for testing
    let reactInternalState = null;
    const fiberRoot = Object.keys(document.querySelector('#__next')).find(key => key.startsWith('__reactContainer$'));
    if (fiberRoot) {
      const stateNodes = [];
      const walkFiber = (fiber) => {
        if (!fiber) return;
        if (fiber.stateNode && fiber.memoizedState) {
          stateNodes.push(fiber.stateNode);
        }
        if (fiber.child) walkFiber(fiber.child);
        if (fiber.sibling) walkFiber(fiber.sibling);
      };
      
      walkFiber(document.querySelector('#__next')[fiberRoot].child);
      // Find component with t as state
      const tComponent = stateNodes.find(
        node => node.state && 
        typeof node.state === 'object' && 
        node.state.t && 
        node.state.t.settings
      );
      
      if (tComponent) {
        reactInternalState = tComponent.state.t;
        console.log('Found translation object:', Object.keys(reactInternalState));
      }
    }
    
    const simulateMissingKey = () => {
      // Save original settings object
      const originalSettings = reactInternalState?.settings;
      
      // Temporarily remove api_diagnostics key
      if (reactInternalState && reactInternalState.settings) {
        const apiDiagnostics = reactInternalState.settings.api_diagnostics;
        delete reactInternalState.settings.api_diagnostics;
        
        console.log('Simulating missing api_diagnostics key...');
        
        // Test accessing with and without optional chaining
        const unsafeAccess = (() => {
          try {
            // This would throw an error without optional chaining
            return reactInternalState.settings.api_diagnostics.title;
          } catch (e) {
            return `ERROR: ${e.message}`;
          }
        })();
        
        const safeAccess = (() => {
          try {
            // This should be undefined but not throw with optional chaining
            return reactInternalState.settings?.api_diagnostics?.title || "Fallback";
          } catch (e) {
            return `ERROR: ${e.message}`;
          }
        })();
        
        console.log('Unsafe access:', unsafeAccess);
        console.log('Safe access with optional chaining:', safeAccess);
        
        // Restore the api_diagnostics key
        if (apiDiagnostics) {
          reactInternalState.settings.api_diagnostics = apiDiagnostics;
        }
      }
    };
    
    if (reactInternalState) {
      simulateMissingKey();
    } else {
      console.log('Could not access React internal state');
    }
    
  } catch (error) {
    console.log(`Error in test: ${error.message}`);
  }
  
  // Now let's verify the UI elements have proper fallback text
  console.log('\n===== UI Fallback Text Check =====');
  const cardTitles = Array.from(document.querySelectorAll('[class*="card-title"]'))
    .map(el => el.textContent);
  
  console.log('Card titles (should show even with missing translations):', cardTitles);
  
  console.log('===== End of Test =====');
  return 'Translation error handling test complete. Check console for results.';
}

// Execute test
testTranslationErrorHandling();

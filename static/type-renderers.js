/**
 * Type-specific renderers for JSON objects
 */

/**
 * Base class for type-specific renderers
 */
export class TypeRenderer {
  /**
   * Creates a new TypeRenderer
   * 
   * @param {JsonRenderer} jsonRenderer - The parent JSON renderer
   */
  constructor(jsonRenderer) {
    this.jsonRenderer = jsonRenderer;
  }
  
  /**
   * Renders an item
   * 
   * @param {Object} item - The item to render
   * @returns {HTMLElement} - The rendered HTML
   */
  render(item) {
    // To be implemented by subclasses
    return null;
  }
}

/**
 * Renderer for real estate listings
 */
export class RealEstateRenderer extends TypeRenderer {
  /**
   * Types that this renderer can handle
   * 
   * @returns {Array<string>} - The types this renderer can handle
   */
  static get supportedTypes() {
    return [
      "SingleFamilyResidence", 
      "Apartment", 
      "Townhouse", 
      "House", 
      "Condominium", 
      "RealEstateListing"
    ];
  }
  
  /**
   * Renders a real estate item
   * 
   * @param {Object} item - The item to render
   * @returns {HTMLElement} - The rendered HTML
   */
  render(item) {
    // Use the default item HTML as a base
    const element = this.jsonRenderer.createDefaultItemHtml(item);
    
    // Find the content div
    const contentDiv = element.querySelector('.item-content');
    if (!contentDiv) return element;
    
    // Add real estate specific details
    const detailsDiv = this.jsonRenderer.possiblyAddExplanation(item, contentDiv, true);
    if (!detailsDiv) return element;
    
    detailsDiv.className = 'item-real-estate-details';
    
    const schema = item.schema_object;
    if (!schema) return element;
    
    const price = schema.price;
    const address = schema.address || {};
    const numBedrooms = schema.numberOfRooms;
    const numBathrooms = schema.numberOfBathroomsTotal;
    const sqft = schema.floorSize?.value;
    
    let priceValue = price;
    if (typeof price === 'object') {
      priceValue = price.price || price.value || price;
      if (typeof priceValue === 'number') {
        priceValue = Math.round(priceValue / 100000) * 100000;
        priceValue = priceValue.toLocaleString('en-US');
      }
    }

    const streetAddress = address.streetAddress || '';
    const addressLocality = address.addressLocality || '';
    detailsDiv.appendChild(this.jsonRenderer.makeAsSpan(`${streetAddress}, ${addressLocality}`));
    detailsDiv.appendChild(document.createElement('br'));
    
    const bedroomsText = numBedrooms || '0';
    const bathroomsText = numBathrooms || '0';
    const sqftText = sqft || '0';
    detailsDiv.appendChild(this.jsonRenderer.makeAsSpan(`${bedroomsText} bedrooms, ${bathroomsText} bathrooms, ${sqftText} sqft`));
    detailsDiv.appendChild(document.createElement('br'));
    
    if (priceValue) {
      detailsDiv.appendChild(this.jsonRenderer.makeAsSpan(`Listed at ${priceValue}`));
    }
    
    return element;
  }
}

/**
 * Renderer for podcast episodes
 */
export class PodcastEpisodeRenderer extends TypeRenderer {
  /**
   * Types that this renderer can handle
   * 
   * @returns {Array<string>} - The types this renderer can handle
   */
  static get supportedTypes() {
    return ["PodcastEpisode"];
  }
  
  /**
   * Renders a podcast episode item
   * 
   * @param {Object} item - The item to render
   * @returns {HTMLElement} - The rendered HTML
   */
  render(item) {
    // Use the default item HTML as a base
    const element = this.jsonRenderer.createDefaultItemHtml(item);
    
    // Find the content div
    const contentDiv = element.querySelector('.item-content');
    if (!contentDiv) return element;
    
    // Add podcast specific details - in this case just ensure explanation is shown
    this.jsonRenderer.possiblyAddExplanation(item, contentDiv, true);
    
    return element;
  }
}

/**
 * Renderer for statutes
 */
export class StatuteRenderer extends TypeRenderer {
  /**
   * Types that this renderer can handle
   * 
   * @returns {Array<string>} - The types this renderer can handle
   */
  static get supportedTypes() {
    return ["Statute"];
  }
  
  /**
   * Renders a statute item
   * 
   * @param {Object} item - The statute item to render
   * @returns {HTMLElement} - The rendered HTML
   */
  render(item) {
    // Use the default renderer but with a custom title
    const container = this.jsonRenderer.createDefaultItemHtml(item);
    
    // Find the title link and its parent
    const titleLink = container.querySelector('.item-title-link');
    const titleRow = container.querySelector('.item-title-row');
    
    if (titleLink && titleRow) {
      // Set the main title (just the statute name)
      titleLink.textContent = item.name || 'Untitled Statute';
      
      // Create a subtle metadata line below the title
      const metadataDiv = document.createElement('div');
      metadataDiv.style.cssText = `
        font-size: 0.85em;
        color: #666;
        margin-top: 4px;
        display: flex;
        gap: 12px;
        align-items: center;
      `;
      
      // Add state with a location icon feel
      if (item.schema_object.state) {
        const stateSpan = document.createElement('span');
        stateSpan.textContent = item.schema_object.state;
        stateSpan.style.cssText = 'font-weight: 500;';
        metadataDiv.appendChild(stateSpan);
      }
      
      // Add year with a bullet separator
      if (item.schema_object.year) {
        if (item.schema_object.state) {
          const separator = document.createElement('span');
          separator.textContent = '•';
          separator.style.cssText = 'color: #ccc;';
          metadataDiv.appendChild(separator);
        }
        const yearSpan = document.createElement('span');
        yearSpan.textContent = item.schema_object.year;
        metadataDiv.appendChild(yearSpan);
      }
      
      // Add citation in a muted style
      if (item.schema_object.citation) {
        if (item.schema_object.state || item.schema_object.year) {
          const separator = document.createElement('span');
          separator.textContent = '•';
          separator.style.cssText = 'color: #ccc;';
          metadataDiv.appendChild(separator);
        }
        const citationSpan = document.createElement('span');
        citationSpan.textContent = item.schema_object.citation;
        citationSpan.style.cssText = 'font-style: italic;';
        metadataDiv.appendChild(citationSpan);
      }
      
      // Insert metadata after the title row
      titleRow.parentNode.insertBefore(metadataDiv, titleRow.nextSibling);
    }
    
    return container;
  }
}

/**
 * Factory for creating type renderers
 */
export class TypeRendererFactory {
  /**
   * Registers all type renderers with a JSON renderer
   * 
   * @param {JsonRenderer} jsonRenderer - The JSON renderer to register with
   */
  static registerAll(jsonRenderer) {
    TypeRendererFactory.registerRenderer(RealEstateRenderer, jsonRenderer);
    TypeRendererFactory.registerRenderer(PodcastEpisodeRenderer, jsonRenderer);
    TypeRendererFactory.registerRenderer(StatuteRenderer, jsonRenderer);
    // RecipeRenderer will be registered separately
    // Add more renderers here as needed
  }
  
  /**
   * Registers a specific renderer with a JSON renderer
   * 
   * @param {Function} RendererClass - The renderer class
   * @param {JsonRenderer} jsonRenderer - The JSON renderer to register with
   */
  static registerRenderer(RendererClass, jsonRenderer) {
    const renderer = new RendererClass(jsonRenderer);
    
    RendererClass.supportedTypes.forEach(type => {
      jsonRenderer.registerTypeRenderer(type, (item) => renderer.render(item));
    });
  }
}
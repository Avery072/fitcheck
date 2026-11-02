// Example clothing items for testing virtual try-on
// Note: These are placeholder URLs - replace with actual accessible image URLs
export const exampleItems = [
  {
    title: 'Black Hoodie',
    imageUrl: 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400',
    category: 'hoodie',
    retailer: 'example'
  },
  {
    title: 'White T-Shirt',
    imageUrl: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400',
    category: 'shirt',
    retailer: 'example'
  },
  {
    title: 'Blue Jeans',
    imageUrl: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400',
    category: 'jeans',
    retailer: 'example'
  },
  {
    title: 'Denim Jacket',
    imageUrl: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400',
    category: 'jacket',
    retailer: 'example'
  },
  {
    title: 'Gray Sweater',
    imageUrl: 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400',
    category: 'sweater',
    retailer: 'example'
  },
  {
    title: 'Black Pants',
    imageUrl: 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400',
    category: 'pants',
    retailer: 'example'
  }
];

// Categories mapping to Bedrock garment classes
export const categoryToGarmentClass = {
  pants: 'LOWER_BODY',
  jeans: 'LOWER_BODY',
  trousers: 'LOWER_BODY',
  shorts: 'LOWER_BODY',
  dress: 'FULL_BODY',
  jumpsuit: 'FULL_BODY',
  // Everything else is UPPER_BODY
  shirt: 'UPPER_BODY',
  top: 'UPPER_BODY',
  blouse: 'UPPER_BODY',
  hoodie: 'UPPER_BODY',
  jacket: 'UPPER_BODY',
  coat: 'UPPER_BODY',
  sweater: 'UPPER_BODY'
};

export const validCategories = Object.keys(categoryToGarmentClass);

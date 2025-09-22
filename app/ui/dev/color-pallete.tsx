'use client';

import { Heading, Text, Box, Card, Flex, Grid } from '@radix-ui/themes';

interface ColorSwatch {
  color: string;
  label: string;
  textColor?: string;
}

const ColorPalette = () => {
  const logoColors = [
    { color: 'var(--logo-deep-color)', label: 'Logo Deep (#0A5E5C)', textColor: 'white' },
    { color: 'var(--logo-mid-color)', label: 'Logo Mid (#16A396)', textColor: 'white' },
    { color: 'var(--logo-light-color)', label: 'Logo Light (#21DDB8)', textColor: 'black' },
  ];

  const mintScale = [
    { color: 'var(--mint-1)', label: 'Mint 1', textColor: 'black' },
    { color: 'var(--mint-2)', label: 'Mint 2', textColor: 'black' },
    { color: 'var(--mint-3)', label: 'Mint 3', textColor: 'black' },
    { color: 'var(--mint-4)', label: 'Mint 4', textColor: 'black' },
    { color: 'var(--mint-5)', label: 'Mint 5', textColor: 'black' },
    { color: 'var(--mint-6)', label: 'Mint 6', textColor: 'black' },
    { color: 'var(--mint-7)', label: 'Mint 7', textColor: 'black' },
    { color: 'var(--mint-8)', label: 'Mint 8 (Light)', textColor: 'black' },
    { color: 'var(--mint-9)', label: 'Mint 9 (Mid)', textColor: 'white' },
    { color: 'var(--mint-10)', label: 'Mint 10', textColor: 'white' },
    { color: 'var(--mint-11)', label: 'Mint 11 (Deep)', textColor: 'white' },
    { color: 'var(--mint-12)', label: 'Mint 12', textColor: 'white' },
  ];

  const semanticColors = [
    { color: 'var(--color-background)', label: 'Background', textColor: 'var(--color-foreground)' },
    { color: 'var(--color-foreground)', label: 'Foreground', textColor: 'var(--color-background)' },
    { color: 'var(--color-border)', label: 'Border', textColor: 'black' },
    { color: 'var(--color-accent)', label: 'Accent', textColor: 'white' },
  ];

  const renderColorSwatch = (swatch: ColorSwatch) => (
    <Card key={swatch.label} style={{ padding: 0, overflow: 'hidden' }}>
      <Flex direction="column" align="center">
        <Box 
          style={{ 
            backgroundColor: swatch.color, 
            width: '100%', 
            height: '100px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: swatch.textColor || 'inherit',
            padding: '8px'
          }}
        >
          <Text weight="bold" align="center">{swatch.label}</Text>
        </Box>
      </Flex>
    </Card>
  );

  return (
    <Box className="color-palette" p="4">
      <Heading size="5" mb="4">Logo Colors</Heading>
      <Grid columns={{ initial: '1', sm: '2', md: '3' }} gap="3" mb="6">
        {logoColors.map(renderColorSwatch)}
      </Grid>

      <Heading size="5" mb="4">Mint Color Scale</Heading>
      <Grid columns={{ initial: '1', sm: '3', md: '4' }} gap="3" mb="6">
        {mintScale.map(renderColorSwatch)}
      </Grid>

      <Heading size="5" mb="4">Semantic Colors</Heading>
      <Grid columns={{ initial: '1', sm: '2', md: '4' }} gap="3" mb="6">
        {semanticColors.map(renderColorSwatch)}
      </Grid>

      <Box mt="6" p="4" style={{ backgroundColor: 'var(--color-background)', border: '1px solid var(--color-border)' }}>
        <Heading size="4" mb="2" style={{ color: 'var(--color-foreground)' }}>
          Current Theme Preview
        </Heading>
        <Text style={{ color: 'var(--color-foreground)' }}>
          This box shows your current theme colors for background, text, and borders.
        </Text>
      </Box>
    </Box>
  );
};

export default ColorPalette;
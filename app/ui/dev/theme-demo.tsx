'use client';

import { 
  Box, 
  Button, 
  Card, 
  Flex, 
  Heading, 
  Text, 
  TextField, 
  Select, 
  Grid, 
  Dialog, 
  IconButton, 
  Separator 
} from '@radix-ui/themes';
import { MixerHorizontalIcon, GearIcon, PlusIcon } from '@radix-ui/react-icons';

const ThemeDemo = () => {
  return (
    <Box p="6">
      <Heading size="6" mb="4">Design System Components</Heading>
      <Text mb="6">This page demonstrates Radix UI components styled with your custom theme.</Text>
      
      <Grid columns={{ initial: '1', md: '2' }} gap="6" mb="8">
        <Card>
          <Flex direction="column" gap="4">
            <Heading size="4">Buttons</Heading>
            <Separator size="4" />
            <Flex gap="4" wrap="wrap">
              <Button>Default Button</Button>
              <Button variant="soft">Soft Button</Button>
              <Button variant="outline">Outline Button</Button>
              <Button variant="ghost">Ghost Button</Button>
            </Flex>
            
            <Heading size="4" mt="2">Icon Buttons</Heading>
            <Separator size="4" />
            <Flex gap="4">
              <IconButton>
                <GearIcon />
              </IconButton>
              <IconButton variant="soft">
                <MixerHorizontalIcon />
              </IconButton>
              <IconButton variant="outline">
                <PlusIcon />
              </IconButton>
            </Flex>
          </Flex>
        </Card>
        
        <Card>
          <Flex direction="column" gap="4">
            <Heading size="4">Form Controls</Heading>
            <Separator size="4" />
            <TextField.Root placeholder="Enter text here..." />
            
            <Select.Root defaultValue="option1">
              <Select.Trigger />
              <Select.Content>
                <Select.Item value="option1">Option 1</Select.Item>
                <Select.Item value="option2">Option 2</Select.Item>
                <Select.Item value="option3">Option 3</Select.Item>
              </Select.Content>
            </Select.Root>
            
            <Dialog.Root>
              <Dialog.Trigger>
                <Button>Open Dialog</Button>
              </Dialog.Trigger>
              <Dialog.Content>
                <Dialog.Title>Sample Dialog</Dialog.Title>
                <Dialog.Description size="2" mb="4">
                  This dialog is styled using your custom theme.
                </Dialog.Description>
                
                <Flex gap="3" mt="4" justify="end">
                  <Dialog.Close>
                    <Button variant="soft" color="gray">Cancel</Button>
                  </Dialog.Close>
                  <Dialog.Close>
                    <Button>Save Changes</Button>
                  </Dialog.Close>
                </Flex>
              </Dialog.Content>
            </Dialog.Root>
          </Flex>
        </Card>
      </Grid>
      
      <Card>
        <Heading size="4" mb="4">Color Samples</Heading>
        <Separator size="4" mb="4" />
        <Grid columns={{ initial: '2', sm: '3', md: '6' }} gap="3">
          {['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'].map((step) => (
            <Flex key={step} direction="column" align="center">
              <Box 
                style={{ 
                  width: '100%', 
                  height: '60px', 
                  backgroundColor: `var(--mint-${step})`,
                  borderRadius: 'var(--radius-2)',
                  marginBottom: 'var(--space-1)'
                }} 
              />
              <Text size="1">Mint {step}</Text>
            </Flex>
          ))}
        </Grid>
      </Card>
    </Box>
  );
};

export default ThemeDemo;
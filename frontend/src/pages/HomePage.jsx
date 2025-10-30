import { Link as RouterLink } from 'react-router-dom'
import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react'

function HomePage() {
  return (
    <Box textAlign="center" py={20} bg="gray.50" minH="100vh">
      <VStack spacing={6}>
        <Heading>Welcome to the Map Quiz App</Heading>
        <Text>Select a city to start</Text>
        <Button as={RouterLink} to="/san-diego" colorScheme="blue" size="lg">
          Go to San Diego
        </Button>
      </VStack>
    </Box>
  )
}

export default HomePage

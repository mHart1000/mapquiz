import { Link as RouterLink } from 'react-router-dom'
import { Heading, Text, Button, VStack } from '@chakra-ui/react'
import Layout from '../components/Layout'

function HomePage() {
  return (
    <Layout>
      <VStack spacing={6} align="center">
        <Heading>Welcome to the Map Quiz App</Heading>
        <Text>Select a city to start</Text>
        <Button as={RouterLink} to="/san-diego" colorScheme="blue" size="lg">
          Go to San Diego
        </Button>
      </VStack>
    </Layout>
  )
}

export default HomePage

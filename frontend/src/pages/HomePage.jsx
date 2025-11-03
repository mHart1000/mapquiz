import { Link as RouterLink } from 'react-router-dom'
import { Heading, Text, Button, VStack } from '@chakra-ui/react'
import Layout from '../components/Layout'

function HomePage() {
  return (
    <Layout>
      <VStack spacing={6} align="center">
        <Heading>Map Quiz App</Heading>
        <Text>Cities</Text>
        <Button as={RouterLink} to="/san-diego" colorScheme="blue" size="lg">
          San Diego
        </Button>
        <Button colorScheme="blue" size="lg">
          Chicago
        </Button>
        <Button colorScheme="blue" size="lg">
          New York
        </Button>
        <Button as={RouterLink} to="/los-angeles" colorScheme="blue" size="lg">
          Los Angeles
        </Button>
      </VStack>
    </Layout>
  )
}

export default HomePage

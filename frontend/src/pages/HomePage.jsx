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
        <Button colorScheme="blue" size="lg" isDisabled>
          Chicago (coming soon)
        </Button>
        <Button colorScheme="blue" size="lg" isDisabled>
          New York (coming soon)
        </Button>
        <Button colorScheme="blue" size="lg" isDisabled>
          Los Angeles (coming soon)
        </Button>
      </VStack>
    </Layout>
  )
}

export default HomePage
